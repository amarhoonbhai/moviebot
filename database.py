from motor.motor_asyncio import AsyncIOMotorClient
from config import DATABASE_URL, DATABASE_NAME
from datetime import datetime
from bson import ObjectId

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(DATABASE_URL)
        self.db = self.client[DATABASE_NAME]
        self.files = self.db.files
        self.users = self.db.users

    async def add_user(self, user_id: int):
        """Adds a new user if they don't exist."""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id}},
            upsert=True
        )

    async def get_total_users(self):
        return await self.users.count_documents({})

    async def get_total_files(self):
        return await self.files.count_documents({})

    async def save_file(self, file_data):
        """
        Saves file data to the database.
        file_data: {file_id, message_id, movie_name, year, quality, movie_language, movie_key, size}
        """
        # Ensure unique index on file_id and quality for the same movie_key
        existing = await self.files.find_one({
            "movie_key": file_data["movie_key"],
            "quality": file_data["quality"]
        })
        
        if existing:
            return False # Already exists
        
        file_data["indexed_at"] = datetime.utcnow()
        file_data["search_count"] = 0
        await self.files.insert_one(file_data)
        return True

    async def increment_search(self, movie_key: str):
        """Increments search count for all files of a movie."""
        await self.files.update_many(
            {"movie_key": movie_key},
            {"$inc": {"search_count": 1}}
        )

    async def get_top_movies(self, limit=10):
        """Returns top searched movies grouped by movie_key."""
        pipeline = [
            {"$group": {
                "_id": "$movie_key",
                "movie_name": {"$first": "$movie_name"},
                "year": {"$first": "$year"},
                "total_searches": {"$max": "$search_count"}
            }},
            {"$sort": {"total_searches": -1}},
            {"$limit": limit}
        ]
        cursor = self.files.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def search_movies(self, query: str):
        """
        Search movies by name (case-insensitive partial match).
        Returns grouped results by movie_key.
        """
        cursor = self.files.find({
            "movie_name": {"$regex": query, "$options": "i"}
        }).sort("indexed_at", -1)
        
        results = await cursor.to_list(length=100)
        
        # Group by movie_key
        grouped = {}
        for item in results:
            key = item["movie_key"]
            if key not in grouped:
                grouped[key] = {
                    "movie_name": item["movie_name"],
                    "year": item["year"],
                    "files": []
                }
            grouped[key]["files"].append({
                "quality": item["quality"],
                "language": item["movie_language"],
                "file_id": item["file_id"],
                "message_id": item["message_id"],
                "db_id": str(item["_id"])
            })
            
        return grouped

    async def get_file_by_id(self, file_id: str):
        return await self.files.find_one({"file_id": file_id})

    async def get_file_by_db_id(self, db_id: str):
        return await self.files.find_one({"_id": ObjectId(db_id)})

db = Database()
