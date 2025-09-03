"""
Database Connection Utilities for GitHub Governance Factory
Implementation of database patterns documented in MICROSERVICES-ARCHITECTURE.md
"""

import os
import redis
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB connection for governance rules and configuration"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
        self.database_name = os.getenv('MONGODB_DATABASE', 'governance_factory')
    
    async def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.database = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.database_name}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def get_collection(self, collection_name: str):
        """Get MongoDB collection"""
        if not self.database:
            await self.connect()
        return self.database[collection_name]
    
    async def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        """Insert document into MongoDB collection"""
        collection = await self.get_collection(collection_name)
        document['created_at'] = datetime.utcnow()
        result = await collection.insert_one(document)
        return str(result.inserted_id)
    
    async def find_documents(self, collection_name: str, filter_dict: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Find documents in MongoDB collection"""
        collection = await self.get_collection(collection_name)
        cursor = collection.find(filter_dict or {})
        documents = []
        async for document in cursor:
            document['_id'] = str(document['_id'])  # Convert ObjectId to string
            documents.append(document)
        return documents
    
    async def update_document(self, collection_name: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """Update document in MongoDB collection"""
        collection = await self.get_collection(collection_name)
        update_dict['updated_at'] = datetime.utcnow()
        result = await collection.update_one(filter_dict, {'$set': update_dict})
        return result.modified_count > 0
    
    async def delete_document(self, collection_name: str, filter_dict: Dict[str, Any]) -> bool:
        """Delete document from MongoDB collection"""
        collection = await self.get_collection(collection_name)
        result = await collection.delete_one(filter_dict)
        return result.deleted_count > 0


class SupabaseConnection:
    """Supabase (PostgreSQL) connection for relational data and analytics"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
    
    def connect(self):
        """Establish Supabase connection"""
        try:
            self.client = create_client(self.url, self.key)
            logger.info("Connected to Supabase")
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise
    
    def insert_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert record into Supabase table"""
        if not self.client:
            self.connect()
        
        data['created_at'] = datetime.utcnow().isoformat()
        result = self.client.table(table).insert(data).execute()
        
        if result.data:
            return result.data[0]
        else:
            raise Exception(f"Failed to insert record: {result}")
    
    def select_records(self, table: str, columns: str = "*", filter_conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Select records from Supabase table"""
        if not self.client:
            self.connect()
        
        query = self.client.table(table).select(columns)
        
        if filter_conditions:
            for key, value in filter_conditions.items():
                query = query.eq(key, value)
        
        result = query.execute()
        return result.data
    
    def update_record(self, table: str, data: Dict[str, Any], filter_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Update record in Supabase table"""
        if not self.client:
            self.connect()
        
        data['updated_at'] = datetime.utcnow().isoformat()
        query = self.client.table(table).update(data)
        
        for key, value in filter_conditions.items():
            query = query.eq(key, value)
        
        result = query.execute()
        
        if result.data:
            return result.data[0]
        else:
            raise Exception(f"Failed to update record: {result}")
    
    def delete_record(self, table: str, filter_conditions: Dict[str, Any]) -> bool:
        """Delete record from Supabase table"""
        if not self.client:
            self.connect()
        
        query = self.client.table(table).delete()
        
        for key, value in filter_conditions.items():
            query = query.eq(key, value)
        
        result = query.execute()
        return len(result.data) > 0


class RedisConnection:
    """Redis connection for caching and event streaming"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.password = os.getenv('REDIS_PASSWORD')
        self.db = int(os.getenv('REDIS_DB', 0))
    
    def connect(self):
        """Establish Redis connection"""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True
            )
            
            # Test connection
            self.client.ping()
            logger.info(f"Connected to Redis: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def disconnect(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Redis")
    
    def set_cache(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set cache value with TTL"""
        if not self.client:
            self.connect()
        
        serialized_value = json.dumps(value) if not isinstance(value, str) else value
        self.client.setex(key, ttl_seconds, serialized_value)
    
    def get_cache(self, key: str) -> Any:
        """Get cache value"""
        if not self.client:
            self.connect()
        
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def delete_cache(self, key: str) -> bool:
        """Delete cache key"""
        if not self.client:
            self.connect()
        
        return self.client.delete(key) > 0
    
    def publish_event(self, channel: str, message: Dict[str, Any]):
        """Publish event to Redis channel"""
        if not self.client:
            self.connect()
        
        serialized_message = json.dumps(message)
        self.client.publish(channel, serialized_message)
    
    def subscribe_to_events(self, channels: List[str]):
        """Subscribe to Redis channels"""
        if not self.client:
            self.connect()
        
        pubsub = self.client.pubsub()
        pubsub.subscribe(*channels)
        return pubsub
    
    def set_session(self, session_id: str, session_data: Dict[str, Any], ttl_seconds: int = 86400):
        """Set session data"""
        self.set_cache(f"session:{session_id}", session_data, ttl_seconds)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.get_cache(f"session:{session_id}")
    
    def increment_counter(self, key: str, increment: int = 1) -> int:
        """Increment counter"""
        if not self.client:
            self.connect()
        
        return self.client.incr(key, increment)
    
    def get_counter(self, key: str) -> int:
        """Get counter value"""
        if not self.client:
            self.connect()
        
        value = self.client.get(key)
        return int(value) if value else 0


class DatabaseManager:
    """Centralized database manager for all connections"""
    
    def __init__(self):
        self.mongodb = MongoDBConnection()
        self.supabase = SupabaseConnection()
        self.redis = RedisConnection()
    
    async def initialize_all_connections(self):
        """Initialize all database connections"""
        await self.mongodb.connect()
        self.supabase.connect()
        self.redis.connect()
        logger.info("All database connections initialized")
    
    async def close_all_connections(self):
        """Close all database connections"""
        await self.mongodb.disconnect()
        self.redis.disconnect()
        logger.info("All database connections closed")
    
    def get_mongodb(self) -> MongoDBConnection:
        """Get MongoDB connection"""
        return self.mongodb
    
    def get_supabase(self) -> SupabaseConnection:
        """Get Supabase connection"""
        return self.supabase
    
    def get_redis(self) -> RedisConnection:
        """Get Redis connection"""
        return self.redis


# Global database manager instance
db_manager = DatabaseManager()
