"""
MongoDB Database Connection and Geo-Spatial Index Configuration.
Stores geo-tagged citizen crack/slope-movement photos and crowd-sourced hazard observations.
"""

import os
import json
import math
import asyncio
from typing import Optional, Dict, Any, List
import numpy as np
import pymongo
from pymongo import MongoClient, GEOSPHERE
from motor.motor_asyncio import AsyncIOMotorClient

from backend.config import settings


class MongoDBManager:
    """
    MongoDB Connection and Geospatial Indexing Manager.
    Configured with a 2dsphere spatial index on `location` for geo-tagged citizen observations.
    Provides automatic resilient fallback store if external MongoDB cluster is offline.
    """

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.is_connected = False
        self.fallback_file = os.path.join("data", "citizen_reports_fallback.json")
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(self.fallback_file):
            with open(self.fallback_file, "w") as f:
                json.dump([], f)

    async def connect(self):
        """
        Connects to MongoDB and builds 2dsphere index for geo-tagged queries.
        """
        try:
            print(f"[MongoDB] Connecting to MongoDB cluster at: {settings.MONGODB_URL}...")
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                serverSelectionTimeoutMS=2000,
            )
            # Test connection
            await self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            print(f"[MongoDB] Connected successfully to database: '{settings.MONGODB_DB_NAME}'")

            # Configure GeoJSON 2dsphere index on location field
            collection = self.db[settings.CITIZEN_REPORTS_COLLECTION]
            await collection.create_index([("location", GEOSPHERE)])
            # Unique index on device_report_id to prevent duplicates on bulk reconnect
            await collection.create_index([("device_report_id", pymongo.ASCENDING)], unique=True, sparse=True)
            # Chronological index on device client timestamp for ordering ground truth
            await collection.create_index([("device_id", pymongo.ASCENDING), ("client_timestamp", pymongo.ASCENDING)])
            await collection.create_index([("client_timestamp", pymongo.ASCENDING)])
            print("[MongoDB] Configured 2dsphere index, unique device_report_id index, and chronological timestamp indexes.")

        except Exception as e:
            print(f"[MongoDB Notice] MongoDB cluster unreachable ({e}). Using resilient Local Geospatial Store.")
            self.is_connected = False

    async def insert_citizen_report(self, report_doc: Dict[str, Any]) -> str:
        """
        Inserts geo-tagged citizen crack/slope-movement report.
        """
        # Ensure GeoJSON structure: { "type": "Point", "coordinates": [longitude, latitude] }
        if "location" not in report_doc and "latitude" in report_doc and "longitude" in report_doc:
            report_doc["location"] = {
                "type": "Point",
                "coordinates": [float(report_doc["longitude"]), float(report_doc["latitude"])]
            }

        if self.is_connected and self.db is not None:
            res = await self.db[settings.CITIZEN_REPORTS_COLLECTION].insert_one(report_doc)
            return str(res.inserted_id)
        else:
            # Fallback to persistent local JSON store
            import uuid
            report_id = str(uuid.uuid4())
            report_doc["_id"] = report_id
            with open(self.fallback_file, "r+") as f:
                data = json.load(f)
                data.append(report_doc)
                f.seek(0)
                json.dump(data, f, indent=2, default=str)
            return report_id

    async def query_nearby_reports(
        self,
        lat: float,
        lon: float,
        radius_km: float = 15.0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Finds citizen crack/subsidence observations within radius_km of a target coordinate.
        """
        radius_meters = radius_km * 1000.0

        if self.is_connected and self.db is not None:
            query = {
                "location": {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": [lon, lat],
                        },
                        "$maxDistance": radius_meters,
                    }
                }
            }
            cursor = self.db[settings.CITIZEN_REPORTS_COLLECTION].find(query).limit(limit)
            reports = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                reports.append(doc)
            return reports
        else:
            # Haversine distance calculation on fallback store
            with open(self.fallback_file, "r") as f:
                data = json.load(f)

            nearby = []
            for item in data:
                coords = item.get("location", {}).get("coordinates", [item.get("longitude", 0), item.get("latitude", 0)])
                item_lon, item_lat = coords[0], coords[1]

                # Haversine formula
                R = 6371.0 # Earth radius km
                dlat = np.radians(item_lat - lat)
                dlon = np.radians(item_lon - lon)
                a = np.sin(dlat / 2)**2 + np.cos(np.radians(lat)) * np.cos(np.radians(item_lat)) * np.sin(dlon / 2)**2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                dist = R * c

                if dist <= radius_km:
                    item_copy = dict(item)
                    item_copy["distance_km"] = round(dist, 2)
                    nearby.append(item_copy)

            nearby.sort(key=lambda x: x.get("distance_km", 0))
            return nearby[:limit]


    async def bulk_upsert_citizen_reports(self, reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk upsert queued reports blasted by offline mobile apps reconnecting to high bandwidth.
        Indexes by original device timestamp and unique device_report_id to prevent duplicates
        and orders ground truth chronologically.
        """
        if not reports:
            return {
                "total_received": 0,
                "upserted_count": 0,
                "modified_count": 0,
                "matched_count": 0,
                "storage_backend": "MongoDB Cluster" if self.is_connected else "Local Fallback",
            }

        operations = []
        for r in reports:
            # Ensure GeoJSON structure
            if "location" not in r and "latitude" in r and "longitude" in r:
                r["location"] = {
                    "type": "Point",
                    "coordinates": [float(r["longitude"]), float(r["latitude"])],
                }

            # Generate or preserve idempotent unique key
            device_report_id = r.get("device_report_id")
            if not device_report_id:
                dev = r.get("device_id", "dev_unknown")
                ts = r.get("client_timestamp", "ts_unknown")
                device_report_id = f"{dev}_{ts}"
                r["device_report_id"] = device_report_id

            # MongoDB UpdateOne upsert filter
            filter_doc = {"device_report_id": device_report_id}
            operations.append(pymongo.UpdateOne(filter_doc, {"$set": r}, upsert=True))

        if self.is_connected and self.db is not None:
            collection = self.db[settings.CITIZEN_REPORTS_COLLECTION]
            result = await collection.bulk_write(operations, ordered=False)
            return {
                "total_received": len(reports),
                "upserted_count": result.upserted_count,
                "modified_count": result.modified_count,
                "matched_count": result.matched_count,
                "storage_backend": "MongoDB Cluster (Bulk Write)",
            }
        else:
            # Atomic Local JSON fallback
            with open(self.fallback_file, "r+") as f:
                try:
                    data = json.load(f)
                except Exception:
                    data = []

                existing_map = {item.get("device_report_id"): i for i, item in enumerate(data) if "device_report_id" in item}
                upserted = 0
                modified = 0

                for r in reports:
                    d_id = r["device_report_id"]
                    if d_id in existing_map:
                        idx = existing_map[d_id]
                        data[idx].update(r)
                        modified += 1
                    else:
                        if "_id" not in r:
                            import uuid
                            r["_id"] = str(uuid.uuid4())
                        data.append(r)
                        existing_map[d_id] = len(data) - 1
                        upserted += 1

                # Chronologically sort by client_timestamp
                data.sort(key=lambda x: str(x.get("client_timestamp", "")))
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2, default=str)

            return {
                "total_received": len(reports),
                "upserted_count": upserted,
                "modified_count": modified,
                "matched_count": modified,
                "storage_backend": "Local Persistent JSON Fallback",
            }

    async def get_chronological_reports(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieves citizen reports ordered chronologically by original client_timestamp.
        """
        if self.is_connected and self.db is not None:
            collection = self.db[settings.CITIZEN_REPORTS_COLLECTION]
            cursor = collection.find().sort("client_timestamp", pymongo.ASCENDING).limit(limit)
            reports = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                reports.append(doc)
            return reports
        else:
            with open(self.fallback_file, "r") as f:
                data = json.load(f)
            data.sort(key=lambda x: str(x.get("client_timestamp", "")))
            return data[:limit]


db_manager = MongoDBManager()


async def get_database():
    return db_manager
