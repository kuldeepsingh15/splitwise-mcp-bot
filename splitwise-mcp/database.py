import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime

class UserDatabase:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table with unique_user_id as primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                unique_user_id TEXT PRIMARY KEY,
                splitwise_user_id INTEGER NOT NULL,
                access_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_token_and_splitwise_id(self, unique_user_id: str) -> Optional[Dict[str, Any]]:
        """Get the splitwise_user_id and access token for a unique user from the database.
        
        Args:
            unique_user_id: The unique user ID to look up
            
        Returns:
            Dict with splitwise_user_id and access_token if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT splitwise_user_id, access_token FROM users WHERE unique_user_id = ?', (unique_user_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {"splitwise_user_id": result[0], "access_token": result[1]}
        else:
            return None
    
    def save_user_token(self, unique_user_id: str, splitwise_user_id: int, access_token: str) -> bool:
        """Save or update a user's splitwise_user_id and access token in the database.
        
        Args:
            unique_user_id: The unique user ID
            splitwise_user_id: The Splitwise user ID
            access_token: The access token to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Use INSERT OR REPLACE to handle both new users and updates
            cursor.execute('''
                INSERT OR REPLACE INTO users (unique_user_id, splitwise_user_id, access_token, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (unique_user_id, splitwise_user_id, access_token))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving user token: {e}")
            return False
    
    def delete_user_token(self, unique_user_id: str) -> bool:
        """Delete a user's access token from the database.
        
        Args:
            unique_user_id: The unique user ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE unique_user_id = ?', (unique_user_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user token: {e}")
            return False
    
    def user_exists(self, unique_user_id: str) -> bool:
        """Check if a user exists in the database.
        
        Args:
            unique_user_id: The unique user ID to check
            
        Returns:
            True if user exists, False otherwise
        """
        return self.get_user_token_and_splitwise_id(unique_user_id) is not None

# Global database instance
db = UserDatabase() 