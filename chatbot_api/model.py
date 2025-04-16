from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
import enum

class user_ip_address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime)

    def __repr__(self):
        return f"user_ip_address('{self.ip_address}', '{self.created_at}')"
    

class role_enum(enum.Enum):
    user = "Human"
    ai = "AI"

class chat_history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    role = db.Column(PGEnum(role_enum, name="role_enum", create_type=True), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime)
