from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, unique=True)
    username = Column(Text, nullable=False)
    first_name = Column(Text, default="")
    last_name = Column(Text, default="")
    last_interaction = Column(DateTime, default=datetime.utcnow)
    first_seen = Column(DateTime, default=datetime.utcnow)
    timestamp = Column(DateTime, default=datetime.utcnow)


class UserDetail(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(String(3), nullable=True, default=None)
    gender = Column(String(10), nullable=True, default=None)
    is_pregrant = Column(Boolean, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Allergy(Base):
    __tablename__ = "allergy"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class MedicalCondition(Base):
    __tablename__ = "medical_condition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Medication(Base):
    __tablename__ = "medication"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Surgery(Base):
    __tablename__ = "surgery"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Issue(Base):
    __tablename__ = "issue"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    clarifying_questions = Column(JSON, nullable=True, default=None)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Medicine(Base):
    __tablename__ = "medicine"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    type = Column(Text, default="")
    minimum_age = Column(Integer, default=0)
    allowed_gender = Column(Text, default="Both")
    is_allowed_for_pregnant = Column(Boolean, default=False)
    avoid_in_allergies = Column(Text, nullable=True, default=None)
    avoid_in_conditions = Column(Text, nullable=True, default=None)
    avoid_in_medications = Column(Text, nullable=True, default=None)
    avoid_in_surgeries = Column(Text, nullable=True, default=None)
    instructions = Column(Text, nullable=True, default=None)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Messages(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_role = Column(Text, nullable=False)
    sender_id = Column(Integer, nullable=True, default=None)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Prescription(Base):
    __tablename__ = "prescription"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detail = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    disease_id = Column(Integer, ForeignKey("issue.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Booking(Base):
    __tablename__ = "booking"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
