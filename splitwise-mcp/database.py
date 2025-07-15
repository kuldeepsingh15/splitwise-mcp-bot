import sqlite3
import os
from typing import Optional, Dict, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDatabase:
    def __init__(self, db_path: str = "users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the users table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table with browser_id as primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                browser_id TEXT PRIMARY KEY,
                splitwise_user_id INTEGER NOT NULL,
                access_token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_token_and_splitwise_id(self, browser_id: str) -> Optional[Dict[str, Any]]:
        """Get the splitwise_user_id and access token for a browser from the database.
        
        Args:
            browser_id: The browser ID to look up
            
        Returns:
            Dict with splitwise_user_id and access_token if found, None otherwise
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT splitwise_user_id, access_token FROM users WHERE browser_id = ?', (browser_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {"splitwise_user_id": result[0], "access_token": result[1]}
        else:
            return None
    
    def save_user_token(self, browser_id: str, splitwise_user_id: int, access_token: str) -> bool:
        """Save or update a browser's splitwise_user_id and access token in the database.
        
        Args:
            browser_id: The browser ID
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
                INSERT OR REPLACE INTO users (browser_id, splitwise_user_id, access_token, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (browser_id, splitwise_user_id, access_token))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error saving user token: {e}")
            return False
    
    def delete_user_token(self, browser_id: str) -> bool:
        """Delete a browser's access token from the database.
        
        Args:
            browser_id: The browser ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE browser_id = ?', (browser_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting user token: {e}")
            return False
    
    def user_exists(self, browser_id: str) -> bool:
        """Check if a browser exists in the database.
        
        Args:
            browser_id: The browser ID to check
            
        Returns:
            True if browser exists, False otherwise
        """
        return self.get_user_token_and_splitwise_id(browser_id) is not None

# Global database instance
db = UserDatabase() 