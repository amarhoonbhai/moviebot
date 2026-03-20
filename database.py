from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME
from datetime import datetime
from bson import ObjectId
import asyncio
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(DATABASE_URL)
        self.db = self.client[DATABASE_NAME]
        # Professional Collections
        self.users = self.db.users
        self.files = self.db.files
        self.search_logs = self.db.search_logs
        self.quiz = self.db.quiz
        self.requests = self.db.requests

    async def fix_indexes(self):
        """Ultra-Professional Index Cleanup & Initialization."""
        try:
            # 1. Sanitize Data: Remove any document with null/missing telegram_user_id
            await self.users.delete_many({"telegram_user_id": None})
            
            # 2. Nuclear Cleanup: Drop all non-primary indexes on users
            indexes = await self.users.index_information()
            for idx_name in list(indexes.keys()):
                if idx_name != "_id_":
                    try:
                        await self.users.drop_index(idx_name)
                        logger.info(f"Dropped legacy index: {idx_name}")
                    except Exception: pass
            
            # 3. Apply Professional Unique Indexes
            await self.users.create_index("telegram_user_id", unique=True)
            await self.files.create_index("file_unique_id", unique=True)
            await self.search_logs.create_index("query", unique=True)
            
            logger.info("Database schema and indexes standardized! 💎")
        except Exception as e:
            logger.error(f"Error during index rebuild: {e}")

    # --- USER MANAGEMENT ---
    async def save_user(self, user):
        """Standardized user save system using upsert and atomic operators."""
        if not user or not user.id: return
        
        await self.users.update_one(
            {"telegram_user_id": user.id},
            {
                "$set": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username
                },
                "$setOnInsert": {
                    "points": 0,
                    "total_searches": 0,
                    "total_downloads": 0,
                    "joined_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    async def update_user_stats(self, user_id: int, points: int = 0, search: bool = False, download: bool = False):
        """Atomic updates for points and activity metrics."""
        update = {"$inc": {"points": points}}
        if search: update["$inc"]["total_searches"] = 1
        if download: update["$inc"]["total_downloads"] = 1
        
        await self.users.update_one({"telegram_user_id": user_id}, update)

    async def get_user_profile(self, user_id: int):
        """Fetches complete profile with rank."""
        user = await self.users.find_one({"telegram_user_id": user_id})
        if not user: return None
        
        # Calculate rank
        rank = await self.users.count_documents({"points": {"$gt": user.get("points", 0)}}) + 1
        user["rank"] = rank
        return user

    async def get_leaderboard(self, limit=10):
        """Top users by points."""
        return await self.users.find().sort("points", -1).limit(limit).to_list(length=limit)

    # --- FILE INDEXING ---
    async def save_file(self, file_data):
        """Saves file with unique constraint validation."""
        try:
            file_data["indexed_at"] = datetime.utcnow()
            await self.files.insert_one(file_data)
            return True
        except Exception: # Duplicate file_unique_id
            return False

    async def search_movies(self, query: str, offset=0, limit=10):
        """Optimized case-insensitive search with pagination."""
        cursor = self.files.find({
            "movie_name": {"$regex": query, "$options": "i"}
        }).sort("indexed_at", -1).skip(offset).limit(limit)
        return await cursor.to_list(length=limit)

    async def get_total_files_count(self, query: str = ""):
        filter_q = {"movie_name": {"$regex": query, "$options": "i"}} if query else {}
        return await self.files.count_documents(filter_q)

    # --- SEARCH LOGS ---
    async def track_search(self, query: str):
        """Numerical tracking of popular queries."""
        await self.search_logs.update_one(
            {"query": query.lower().strip()},
            {"$inc": {"count": 1}},
            upsert=True
        )

    async def get_top_searches(self, limit=10):
        return await self.search_logs.find().sort("count", -1).limit(limit).to_list(length=limit)

    # --- QUIZ SYSTEM ---
    async def get_active_quiz(self):
        return await self.quiz.find_one({"active": True})

    async def create_quiz(self, question, answer, options):
        await self.quiz.update_many({"active": True}, {"$set": {"active": False}})
        await self.quiz.insert_one({
            "question": question,
            "correct_answer": answer,
            "options": options,
            "active": True,
            "answered_by": None,
            "created_at": datetime.utcnow()
        })

    async def claim_quiz(self, quiz_id, user_id):
        """Ensures only the first winner claims the quiz points."""
        result = await self.quiz.update_one(
            {"_id": ObjectId(quiz_id), "active": True, "answered_by": None},
            {"$set": {"answered_by": user_id, "active": False}}
        )
        return result.modified_count > 0

    # --- ADMIN ---
    async def get_total_stats(self):
        return {
            "users": await self.users.count_documents({}),
            "files": await self.files.count_documents({}),
            "searches": await self.search_logs.count_documents({}),
            "top_user": await self.users.find_one(sort=[("points", -1)])
        }

    async def get_all_user_ids(self):
        cursor = self.users.find({}, {"telegram_user_id": 1})
        return [u["telegram_user_id"] for u in await cursor.to_list(length=None)]

    async def save_request(self, query: str, user_id: int):
        await self.requests.insert_one({
            "query": query, "user_id": user_id, "requested_at": datetime.utcnow()
        })

db = Database()
