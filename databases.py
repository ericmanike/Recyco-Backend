from sqlalchemy import JSON, Boolean, Column, Integer, String, ForeignKey, DateTime, UniqueConstraint, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
from config import DATABASE_URL



Base = declarative_base()

engine = create_engine(DATABASE_URL, echo=False)

sessionLocal = sessionmaker(bind=engine)

# ------------------------
# User table
# ------------------------
class users(Base):
    __tablename__ ='users'
    id = Column(Integer, primary_key=True)
    fullName = Column(String)
    email = Column(String, unique=True)
    role = Column(String)
    phone = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    distance = Column(Integer, nullable=True)  # optional field for distance
    location = Column(String, nullable=True)
    about = Column(String, nullable=True)
    images_url = Column(JSON, nullable=True)  # optional, filled after upload

    # relationships
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    conversations1 = relationship("Conversation", foreign_keys="Conversation.user1_id", back_populates="user1")
    conversations2 = relationship("Conversation", foreign_keys="Conversation.user2_id", back_populates="user2")

    notifications = relationship("notifications", back_populates="user", cascade="all, delete-orphan")

    listings_owner = relationship("Listings", back_populates="Listings", cascade="all, delete-orphan")













#---------------------
#Listings talble

class Listings(Base):
    __tablename__ ='listings'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer,ForeignKey('users.id'),nullable=False )
    waste_type =Column(String)
    quantity = Column(String)
    unit = Column(String)
    description = Column(String)
    location = Column(String)
    contactName = Column(String)
    contactEmail = Column(String)
    contactPhone = Column(String)
    hazardous =Column(Boolean, default=False)
    images_url = Column(JSON)

    Listings = relationship("users", back_populates="listings_owner")




# ------------------------
# Conversation table
# ------------------------
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_message = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    user1 = relationship("users", foreign_keys=[user1_id], back_populates="conversations1")
    user2 = relationship("users", foreign_keys=[user2_id], back_populates="conversations2")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # ensure a unique conversation between two users
    __table_args__ = (UniqueConstraint("user1_id", "user2_id", name="unique_conversation"),)


# ------------------------
# Message table
# ------------------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("users", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("users", foreign_keys=[receiver_id], back_populates="received_messages")



# ------------------------
# Notifications table

class notifications(Base):
    __tablename__ ='notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer,ForeignKey('users.id'),nullable=False )
    title = Column(String)
    message = Column(String)
    category = Column(String)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("users", back_populates="notifications")




   
Base.metadata.create_all(bind=engine)
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

