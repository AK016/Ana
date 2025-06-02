#!/usr/bin/env python3
# Ana AI Assistant - Security and Privacy Module

import os
import json
import base64
import logging
import hashlib
import sqlite3
from typing import Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path

# For encryption
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger('Ana.Security')

class SecurityManager:
    """
    Manages security and privacy for all Ana data
    
    Features:
    - Local encryption for all sensitive data
    - No cloud storage of encryption keys
    - Sandboxed data storage
    - Privacy-preserving API calls
    - Secure storage of credentials
    """
    
    def __init__(self, settings: Dict[str, Any]):
        """Initialize the security manager with settings"""
        self.settings = settings
        
        # Initialize encryption
        self.encryption_enabled = settings.get("security", {}).get("encryption_enabled", True)
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.security_dir = os.path.join(self.data_dir, "security")
        
        # Create necessary directories
        os.makedirs(self.security_dir, exist_ok=True)
        
        # Set up encryption key
        self.key_file = os.path.join(self.security_dir, "key.bin")
        self.encryption_key = self._load_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Initialize secure database
        self.db_path = os.path.join(self.security_dir, "secure_data.db")
        self._init_secure_database()
        
        logger.info("Security manager initialized")
    
    def _load_or_create_key(self) -> bytes:
        """Load existing encryption key or create a new one"""
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                logger.info("Loaded existing encryption key")
                return key
            except Exception as e:
                logger.error(f"Error loading encryption key: {str(e)}")
                # If error, create a new key
        
        # Generate a new key
        key = Fernet.generate_key()
        try:
            # Save to file with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)  # Owner read/write only
            logger.info("Created new encryption key")
        except Exception as e:
            logger.error(f"Error saving encryption key: {str(e)}")
        
        return key
    
    def _init_secure_database(self):
        """Initialize the secure SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for various data types
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_credentials (
                service TEXT PRIMARY KEY,
                credentials TEXT,
                last_updated INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                session_id TEXT,
                user_message TEXT,
                assistant_message TEXT,
                metadata TEXT
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                key TEXT PRIMARY KEY,
                value TEXT,
                data_type TEXT,
                last_updated INTEGER
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_tokens (
                repo TEXT PRIMARY KEY,
                token TEXT,
                last_updated INTEGER
            )
            ''')
            
            conn.commit()
            conn.close()
            
            # Set secure permissions
            os.chmod(self.db_path, 0o600)  # Owner read/write only
            logger.info("Secure database initialized")
            
        except sqlite3.Error as e:
            logger.error(f"Error initializing secure database: {str(e)}")
    
    def encrypt(self, data: Union[str, bytes, dict]) -> bytes:
        """Encrypt data with local key"""
        if not self.encryption_enabled:
            if isinstance(data, dict):
                return json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                return data.encode('utf-8')
            return data
            
        try:
            # Convert data to bytes if it's not already
            if isinstance(data, dict):
                data_bytes = json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
                
            # Encrypt the data
            encrypted_data = self.cipher_suite.encrypt(data_bytes)
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            # Fall back to non-encrypted but encoded data
            if isinstance(data, dict):
                return json.dumps(data).encode('utf-8')
            elif isinstance(data, str):
                return data.encode('utf-8')
            return data
    
    def decrypt(self, encrypted_data: bytes) -> Union[str, dict, bytes]:
        """Decrypt data with local key"""
        if not self.encryption_enabled:
            try:
                # Try to decode as JSON
                return json.loads(encrypted_data.decode('utf-8'))
            except:
                # Return as decoded string if not JSON
                try:
                    return encrypted_data.decode('utf-8')
                except:
                    return encrypted_data
                    
        try:
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted_data.decode('utf-8'))
            except:
                # Return as string if not JSON
                try:
                    return decrypted_data.decode('utf-8')
                except:
                    return decrypted_data
                    
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            # Return original data on error
            return encrypted_data
    
    def store_api_credentials(self, service: str, credentials: Dict[str, Any]):
        """Securely store API credentials"""
        try:
            encrypted_credentials = self.encrypt(credentials)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO api_credentials (service, credentials, last_updated) VALUES (?, ?, ?)",
                (service, base64.b64encode(encrypted_credentials).decode('ascii'), int(datetime.now().timestamp()))
            )
            
            conn.commit()
            conn.close()
            logger.info(f"Stored API credentials for {service}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing API credentials for {service}: {str(e)}")
            return False
    
    def get_api_credentials(self, service: str) -> Optional[Dict[str, Any]]:
        """Retrieve API credentials for a service"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT credentials FROM api_credentials WHERE service = ?", (service,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                encrypted_credentials = base64.b64decode(result[0])
                credentials = self.decrypt(encrypted_credentials)
                return credentials
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving API credentials for {service}: {str(e)}")
            return None
    
    def store_conversation(self, user_message: str, assistant_message: str, 
                         session_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Store conversation history securely"""
        try:
            # Create session ID if not provided
            if not session_id:
                session_id = datetime.now().strftime("%Y%m%d%H%M%S")
                
            # Convert metadata to JSON string
            metadata_json = json.dumps(metadata) if metadata else "{}"
            
            # Encrypt all data
            encrypted_user_msg = base64.b64encode(self.encrypt(user_message)).decode('ascii')
            encrypted_assistant_msg = base64.b64encode(self.encrypt(assistant_message)).decode('ascii')
            encrypted_metadata = base64.b64encode(self.encrypt(metadata_json)).decode('ascii')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO conversation_history 
                   (timestamp, session_id, user_message, assistant_message, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (int(datetime.now().timestamp()), session_id, 
                 encrypted_user_msg, encrypted_assistant_msg, encrypted_metadata)
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing conversation: {str(e)}")
            return False
    
    def get_conversations(self, session_id: Optional[str] = None, 
                        limit: int = 100) -> list:
        """Retrieve conversation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if session_id:
                cursor.execute(
                    """SELECT timestamp, user_message, assistant_message, metadata 
                       FROM conversation_history 
                       WHERE session_id = ? 
                       ORDER BY timestamp DESC LIMIT ?""",
                    (session_id, limit)
                )
            else:
                cursor.execute(
                    """SELECT timestamp, session_id, user_message, assistant_message, metadata 
                       FROM conversation_history 
                       ORDER BY timestamp DESC LIMIT ?""",
                    (limit,)
                )
            
            results = cursor.fetchall()
            conn.close()
            
            conversations = []
            for row in results:
                if session_id:
                    timestamp, user_msg, assistant_msg, metadata = row
                    session = session_id
                else:
                    timestamp, session, user_msg, assistant_msg, metadata = row
                
                # Decrypt all data
                try:
                    decrypted_user_msg = self.decrypt(base64.b64decode(user_msg))
                    decrypted_assistant_msg = self.decrypt(base64.b64decode(assistant_msg))
                    decrypted_metadata = self.decrypt(base64.b64decode(metadata))
                    
                    conversations.append({
                        'timestamp': timestamp,
                        'session_id': session,
                        'user_message': decrypted_user_msg,
                        'assistant_message': decrypted_assistant_msg,
                        'metadata': json.loads(decrypted_metadata) if isinstance(decrypted_metadata, str) else decrypted_metadata
                    })
                except Exception as decrypt_error:
                    logger.error(f"Error decrypting conversation data: {str(decrypt_error)}")
            
            return conversations
            
        except Exception as e:
            logger.error(f"Error retrieving conversations: {str(e)}")
            return []
    
    def store_user_data(self, key: str, value: Any, data_type: Optional[str] = None):
        """Securely store user data by key"""
        try:
            # Determine data type if not provided
            if data_type is None:
                data_type = type(value).__name__
                
            # Convert value to string if it's not already
            if isinstance(value, dict) or isinstance(value, list):
                value_str = json.dumps(value)
            else:
                value_str = str(value)
                
            # Encrypt the value
            encrypted_value = base64.b64encode(self.encrypt(value_str)).decode('ascii')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO user_data (key, value, data_type, last_updated) VALUES (?, ?, ?, ?)",
                (key, encrypted_value, data_type, int(datetime.now().timestamp()))
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing user data for key {key}: {str(e)}")
            return False
    
    def get_user_data(self, key: str) -> Optional[Any]:
        """Retrieve user data by key"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT value, data_type FROM user_data WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            conn.close()
            
            if not result:
                return None
                
            encrypted_value, data_type = result
            
            # Decrypt the value
            decrypted_value = self.decrypt(base64.b64decode(encrypted_value))
            
            # Convert back to original type
            if data_type == 'dict' or data_type == 'list':
                return json.loads(decrypted_value) if isinstance(decrypted_value, str) else decrypted_value
            elif data_type == 'int':
                return int(decrypted_value)
            elif data_type == 'float':
                return float(decrypted_value)
            elif data_type == 'bool':
                return decrypted_value.lower() == 'true'
            else:
                return decrypted_value
                
        except Exception as e:
            logger.error(f"Error retrieving user data for key {key}: {str(e)}")
            return None
    
    def store_github_token(self, repo: str, token: str) -> bool:
        """Securely store GitHub token"""
        try:
            encrypted_token = base64.b64encode(self.encrypt(token)).decode('ascii')
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO github_tokens (repo, token, last_updated) VALUES (?, ?, ?)",
                (repo, encrypted_token, int(datetime.now().timestamp()))
            )
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing GitHub token for {repo}: {str(e)}")
            return False
    
    def get_github_token(self, repo: str) -> Optional[str]:
        """Retrieve GitHub token for a repository"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT token FROM github_tokens WHERE repo = ?", (repo,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                encrypted_token = base64.b64decode(result[0])
                token = self.decrypt(encrypted_token)
                return token
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving GitHub token for {repo}: {str(e)}")
            return None
    
    def secure_api_request(self, api_name: str, request_data: Dict[str, Any], 
                         include_credentials: bool = True) -> Dict[str, Any]:
        """Prepare API request with privacy protection"""
        # Create a copy of the request data to avoid modifying the original
        secure_request = request_data.copy()
        
        # Add credentials if requested and available
        if include_credentials:
            credentials = self.get_api_credentials(api_name)
            if credentials:
                # Merge credentials with request data
                secure_request.update(credentials)
        
        # Add privacy measures based on API
        if api_name == "openai":
            # Remove or anonymize any personal identifiers
            if "user" in secure_request:
                # Replace with a consistent but anonymous ID
                user_hash = hashlib.sha256(secure_request["user"].encode()).hexdigest()[:10]
                secure_request["user"] = f"ana_user_{user_hash}"
            
            # Add specific instructions to not store data
            if "messages" in secure_request and isinstance(secure_request["messages"], list):
                # Add privacy instruction as system message
                has_system = False
                for msg in secure_request["messages"]:
                    if msg.get("role") == "system":
                        msg["content"] += " Please do not store, remember, or use this conversation for training."
                        has_system = True
                        break
                
                if not has_system:
                    secure_request["messages"].insert(0, {
                        "role": "system",
                        "content": "Please do not store, remember, or use this conversation for training."
                    })
        
        elif api_name == "elevenlabs":
            # Similar privacy measures for ElevenLabs
            pass
        
        # Add general privacy headers
        if "headers" not in secure_request:
            secure_request["headers"] = {}
        
        secure_request["headers"]["X-Privacy-Requested"] = "no-store, no-log"
        
        return secure_request
    
    def sanitize_response(self, api_name: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize API response to ensure privacy"""
        # Create a copy to avoid modifying the original
        sanitized = response_data.copy()
        
        # Remove sensitive information based on API
        if api_name == "openai":
            # Remove response metadata that might contain identifiers
            if "id" in sanitized:
                del sanitized["id"]
            if "created" in sanitized:
                del sanitized["created"]
            if "usage" in sanitized:
                del sanitized["usage"]
        
        return sanitized
    
    def secure_file_path(self, purpose: str, filename: str) -> str:
        """Get secure file path for storing data"""
        # Create a purpose-specific directory
        purpose_dir = os.path.join(self.data_dir, purpose)
        os.makedirs(purpose_dir, exist_ok=True)
        
        # Create secure file path
        file_path = os.path.join(purpose_dir, filename)
        
        return file_path
    
    def save_encrypted_file(self, data: Union[str, bytes, dict], 
                          purpose: str, filename: str) -> str:
        """Save encrypted data to file"""
        try:
            # Get secure file path
            file_path = self.secure_file_path(purpose, filename)
            
            # Encrypt the data
            encrypted_data = self.encrypt(data)
            
            # Save to file
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set secure permissions
            os.chmod(file_path, 0o600)  # Owner read/write only
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving encrypted file {filename}: {str(e)}")
            return ""
    
    def load_encrypted_file(self, purpose: str, filename: str) -> Union[str, dict, bytes, None]:
        """Load and decrypt file data"""
        try:
            # Get secure file path
            file_path = self.secure_file_path(purpose, filename)
            
            # Check if file exists
            if not os.path.exists(file_path):
                logger.warning(f"Encrypted file not found: {file_path}")
                return None
            
            # Read encrypted data
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted_data = self.decrypt(encrypted_data)
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Error loading encrypted file {filename}: {str(e)}")
            return None
    
    def wipe_all_data(self, confirm: bool = False) -> bool:
        """Wipe all stored data (for privacy or security reasons)"""
        if not confirm:
            logger.warning("Data wipe requested but not confirmed")
            return False
        
        try:
            # Delete database
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
            
            # Reinitialize database
            self._init_secure_database()
            
            logger.info("All secure data wiped successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error wiping data: {str(e)}")
            return False
    
    def generate_privacy_report(self) -> Dict[str, Any]:
        """Generate a report on stored data for transparency"""
        report = {
            "report_time": datetime.now().isoformat(),
            "encryption_enabled": self.encryption_enabled,
            "data_counts": {},
            "data_types": {}
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count conversation history
            cursor.execute("SELECT COUNT(*) FROM conversation_history")
            report["data_counts"]["conversations"] = cursor.fetchone()[0]
            
            # Count API credentials
            cursor.execute("SELECT COUNT(*), GROUP_CONCAT(service) FROM api_credentials")
            count, services = cursor.fetchone()
            report["data_counts"]["api_credentials"] = count
            report["data_types"]["api_services"] = services.split(",") if services else []
            
            # Count user data
            cursor.execute("SELECT COUNT(*), GROUP_CONCAT(key) FROM user_data")
            count, keys = cursor.fetchone()
            report["data_counts"]["user_data"] = count
            report["data_types"]["user_data_keys"] = keys.split(",") if keys else []
            
            # Count GitHub tokens
            cursor.execute("SELECT COUNT(*) FROM github_tokens")
            report["data_counts"]["github_tokens"] = cursor.fetchone()[0]
            
            conn.close()
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating privacy report: {str(e)}")
            return {
                "error": str(e),
                "report_time": datetime.now().isoformat()
            } 