import psycopg2 # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import time

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        """Initialize database connection"""
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create required tables if they do not exist"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """
        
        create_otp_table = """
        CREATE TABLE IF NOT EXISTS otp_store (
            email VARCHAR(255) NOT NULL,
            otp VARCHAR(6) NOT NULL,
            timestamp BIGINT NOT NULL
        );
        """
        
        self.cursor.execute(create_users_table)
        self.cursor.execute(create_otp_table)
        self.conn.commit()

    def insert_user(self, username, email, password):
        """Insert a new user into the database"""
        try:
            self.cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) ON CONFLICT(email) DO NOTHING",
                (username, email, password)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting user: {e}")
            return False

    def get_user_by_email(self, email):
        """Retrieve user details by email"""
        self.cursor.execute("SELECT id, password FROM users WHERE email=%s", (email,))
        return self.cursor.fetchone()
    
    def store_otp(self, email, otp):
        """Store OTP for password reset"""
        # Delete any existing OTP for this email
        self.cursor.execute("DELETE FROM otp_store WHERE email=%s", (email,))
        
        # Store new OTP with current timestamp
        current_time = int(time.time())
        self.cursor.execute(
            "INSERT INTO otp_store (email, otp, timestamp) VALUES (%s, %s, %s)",
            (email, otp, current_time)
        )
        self.conn.commit()
        return True
    
    def verify_otp(self, email, otp):
        """Verify OTP for password reset"""
        # OTPs expire after 10 minutes (600 seconds)
        expiry_time = int(time.time()) - 600
        
        self.cursor.execute(
            "SELECT otp FROM otp_store WHERE email=%s AND otp=%s AND timestamp > %s",
            (email, otp, expiry_time)
        )
        
        result = self.cursor.fetchone()
        
        if result:
            # Clean up the used OTP
            self.cursor.execute("DELETE FROM otp_store WHERE email=%s", (email,))
            self.conn.commit()
            return True
        
        return False
    
    def update_password(self, email, new_password):
        """Update user password"""
        try:
            self.cursor.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (new_password, email)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating password: {e}")
            return False

    def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

# Initialize DatabaseManager globally
db = DatabaseManager()