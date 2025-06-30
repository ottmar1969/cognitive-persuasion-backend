from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import hashlib
import uuid as python_uuid
from enum import Enum

db = SQLAlchemy()

# Simple password hashing without bcrypt
def hash_password(password):
    """Simple password hashing using hashlib"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password(password, hashed):
    """Check password against hash"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed

class SessionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class TransactionType(Enum):
    PURCHASE = "purchase"
    CONSUMPTION = "consumption"
    REFUND = "refund"

class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    credit_balance = db.Column(db.Integer, default=0)  # Credits available
    
    # Relationships
    business_types = db.relationship('BusinessType', backref='user', lazy=True, cascade='all, delete-orphan')
    target_audiences = db.relationship('TargetAudience', backref='user', lazy=True, cascade='all, delete-orphan')
    ai_sessions = db.relationship('AISession', backref='user', lazy=True, cascade='all, delete-orphan')
    credit_transactions = db.relationship('CreditTransaction', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Check password"""
        return check_password(password, self.password_hash)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'credit_balance': self.credit_balance
        }

class BusinessType(db.Model):
    __tablename__ = 'business_types'
    
    business_type_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    industry_category = db.Column(db.String(255))
    is_custom = db.Column(db.Boolean, default=True)  # True for user-created, False for predefined
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'business_type_id': self.business_type_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'industry_category': self.industry_category,
            'is_custom': self.is_custom,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TargetAudience(db.Model):
    __tablename__ = 'target_audiences'
    
    audience_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    manual_description = db.Column(db.Text)  # For manual audience input
    is_custom = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'audience_id': self.audience_id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'manual_description': self.manual_description,
            'is_custom': self.is_custom,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AISession(db.Model):
    __tablename__ = 'ai_sessions'
    
    session_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    business_type_id = db.Column(db.String(36), db.ForeignKey('business_types.business_type_id'), nullable=False)
    audience_id = db.Column(db.String(36), db.ForeignKey('target_audiences.audience_id'), nullable=False)
    mission_objective = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(SessionStatus), default=SessionStatus.PENDING)
    credits_consumed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    messages = db.relationship('AIMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'business_type_id': self.business_type_id,
            'audience_id': self.audience_id,
            'mission_objective': self.mission_objective,
            'status': self.status.value if self.status else None,
            'credits_consumed': self.credits_consumed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AIMessage(db.Model):
    __tablename__ = 'ai_messages'
    
    message_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('ai_sessions.session_id'), nullable=False)
    agent_type = db.Column(db.String(50), nullable=False)  # logic, emotion, creative, authority, social_proof
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'message_id': self.message_id,
            'session_id': self.session_id,
            'agent_type': self.agent_type,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CreditTransaction(db.Model):
    __tablename__ = 'credit_transactions'
    
    transaction_id = db.Column(db.String(36), primary_key=True, default=lambda: str(python_uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.user_id'), nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Credits amount (positive for purchase, negative for consumption)
    price = db.Column(db.Numeric(10, 2))  # Price in USD for purchases
    status = db.Column(db.Enum(TransactionStatus), default=TransactionStatus.PENDING)
    paypal_order_id = db.Column(db.String(255))  # PayPal order ID
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Additional metadata for transaction details
    transaction_metadata = db.Column(db.JSON)  # Store additional transaction details
    
    def to_dict(self):
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'transaction_type': self.transaction_type.value if self.transaction_type else None,
            'amount': self.amount,
            'price': float(self.price) if self.price else None,
            'status': self.status.value if self.status else None,
            'paypal_order_id': self.paypal_order_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.transaction_metadata
        }

