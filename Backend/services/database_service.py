from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional, Dict, List
from datetime import datetime
from config import Config
import time

class DatabaseService:
    """Service class for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.queries_collection: Optional[Collection] = None
        self.users_collection: Optional[Collection] = None
        self.history_collection: Optional[Collection] = None
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB with retry logic"""
        max_retries = 3
        retry_delay = 2
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                print(f"🔌 Connecting to MongoDB (Attempt {attempt}/{max_retries})...")
                
                # MongoDB connection with Python 3.13 compatible settings
                connection_string = Config.MONGO_URI
                if "?" in connection_string:
                    connection_string += "&tlsAllowInvalidCertificates=true"
                else:
                    connection_string += "?tlsAllowInvalidCertificates=true"
                
                self.client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=10000,
                    connectTimeoutMS=20000,
                    socketTimeoutMS=20000,
                    retryWrites=True,
                    retryReads=True,
                    maxPoolSize=50,
                    minPoolSize=10,
                    maxIdleTimeMS=45000,
                    waitQueueTimeoutMS=10000,
                    appname='HealthSymptomChecker'
                )
                
                # Test connection
                print(f"   Testing connection...")
                self.client.admin.command('ping', maxTimeMS=5000)
                print(f"✓ MongoDB connection successful!")
            
                self.db = self.client.get_database("health_symptom_checker")
                self.queries_collection = self.db["queries"]
                self.users_collection = self.db["users"]
                self.history_collection = self.db["symptom_history"]
                
                print(f"✓ Database: {self.db.name}")
                
                # Create indexes for better performance
                print(f"   Creating indexes...")
                try:
                    self.users_collection.create_index("email", unique=True)
                    self.history_collection.create_index([("user_id", 1), ("created_at", -1)])
                    print(f"✓ Indexes created successfully")
                except Exception as idx_error:
                    print(f"⚠️  Index creation warning: {idx_error}")
                
                print(f"✓ Collections initialized: users, symptom_history, queries")
                print(f"=" * 70)
                return  # Success, exit function
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                last_error = e
                print(f"❌ Connection attempt {attempt} failed: {e}")
                
                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ All {max_retries} connection attempts failed")
                    
            except Exception as e:
                last_error = e
                print(f"❌ Unexpected error during MongoDB connection: {e}")
                if attempt < max_retries:
                    time.sleep(retry_delay)
                else:
                    break
        
        # If we get here, all retries failed
        print(f"\n{'='*70}")
        print(f"⚠️  MongoDB Connection Failed After {max_retries} Attempts")
        print(f"{'='*70}")
        print(f"Last Error: {last_error}")
        print(f"\n💡 Quick Fixes:")
        print(f"   1. Check MongoDB Atlas Network Access (allow 0.0.0.0/0)")
        print(f"   2. Verify .env has correct MONGO_URI")
        print(f"   3. Check internet connection")
        print(f"   4. Try: tlsAllowInvalidCertificates=true in URI")
        print(f"{'='*70}\n")
        print("⚠️  The application will continue without database functionality.")
        print("⚠️  Authentication and history features will not work.\n")
        
        # Don't raise - allow app to continue without MongoDB
        self.client = None
        self.db = None
        self.queries_collection = None
        self.users_collection = None
        self.history_collection = None
    
    def save_query(self, symptoms: str, conditions: List[str], recommendations: List[str], 
                   user_id: Optional[str] = None) -> str:
        """
        Save a symptom query to the database
        
        Args:
            symptoms: User input symptoms
            conditions: List of probable conditions
            recommendations: List of recommended next steps
            user_id: Optional user identifier
        
        Returns:
            Query document ID
        """
        if self.queries_collection is None:
            print("MongoDB not connected. Query not saved.")
            return "no-db-connection"
            
        query_doc = {
            "symptoms": symptoms,
            "conditions": conditions,
            "recommendations": recommendations,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = self.queries_collection.insert_one(query_doc)
        return str(result.inserted_id)
    
    def get_query_history(self, user_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Retrieve query history
        
        Args:
            user_id: Optional user identifier to filter queries
            limit: Maximum number of queries to return
        
        Returns:
            List of query documents
        """
        if self.queries_collection is None:
            print("MongoDB not connected. Returning empty history.")
            return []
            
        query_filter = {}
        if user_id:
            query_filter["user_id"] = user_id
        
        queries = self.queries_collection.find(query_filter).sort("timestamp", -1).limit(limit)
        return list(queries)
    
    def get_query_by_id(self, query_id: str) -> Optional[Dict]:
        """
        Retrieve a specific query by ID
        
        Args:
            query_id: MongoDB document ID
        
        Returns:
            Query document or None if not found
        """
        if self.queries_collection is None:
            print("MongoDB not connected. Cannot retrieve query.")
            return None
            
        from bson import ObjectId
        try:
            return self.queries_collection.find_one({"_id": ObjectId(query_id)})
        except Exception:
            return None
    
    # User Management Methods
    def create_user(self, email: str, hashed_password: str, full_name: str) -> Optional[str]:
        """Create a new user"""
        if self.users_collection is None:
            return None
        
        user_doc = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "created_at": datetime.utcnow(),
            "is_active": True
        }
        
        try:
            result = self.users_collection.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if self.users_collection is None:
            return None
        return self.users_collection.find_one({"email": email})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        if self.users_collection is None:
            return None
        from bson import ObjectId
        try:
            return self.users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
    
    # Symptom History Methods
    def save_symptom_history(self, user_id: str, symptoms: str, severity: str, 
                            conditions: List[str], recommendations: List[str],
                            image_analysis: Optional[str] = None,
                            image_filename: Optional[str] = None,
                            pdf_name: Optional[str] = None) -> Optional[str]:
        """Save symptom analysis to user history"""
        if self.history_collection is None:
            return None
        
        history_doc = {
            "user_id": user_id,
            "symptoms": symptoms,
            "severity": severity,
            "conditions": conditions,
            "recommendations": recommendations,
            "image_analysis": image_analysis,
            "image_filename": image_filename,
            "pdf_name": pdf_name,
            "created_at": datetime.utcnow()
        }
        
        try:
            result = self.history_collection.insert_one(history_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error saving symptom history: {e}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get symptom history for a user"""
        if self.history_collection is None:
            return []
        
        try:
            history = self.history_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
            return list(history)
        except Exception as e:
            print(f"Error fetching user history: {e}")
            return []
    
    def get_history_by_id(self, history_id: str) -> Optional[Dict]:
        """Get specific history entry by ID"""
        if self.history_collection is None:
            return None
        
        from bson import ObjectId
        try:
            return self.history_collection.find_one({"_id": ObjectId(history_id)})
        except Exception:
            return None
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()


