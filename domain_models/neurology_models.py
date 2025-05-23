from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from database.database import Base


class PredictedNeurologyReportRecord(Base):
    __tablename__ = 'predicted_neurology_reports'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=False)
    full_report = Column(JSONB, nullable=False)
    phase = Column(String, nullable=False)
    real_report_id = Column(Integer, ForeignKey("neurology_reports.id"), nullable=True)
    real_report = relationship("NeurologyReportRecord", back_populates="generated_reports")


class NeurologyReportRecord(Base):
    __tablename__ = 'neurology_reports'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    summary = Column(Text, nullable=False)
    full_report = Column(JSONB, nullable=False)
    generated_reports = relationship("PredictedNeurologyReportRecord", back_populates="real_report")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    questions = relationship("Question", back_populates="metric", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    text = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    metric = relationship("Metric", back_populates="questions")


class ReportKey(Base):
    __tablename__ = "report_keys"
    id = Column(Integer, primary_key=True)
    key_path = Column(String, nullable=False, unique=True)


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_report_id = Column(Integer, ForeignKey("predicted_neurology_reports.id"), nullable=False)
    report_key_id = Column(Integer, ForeignKey("report_keys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    predicted_report = relationship("PredictedNeurologyReportRecord")
    report_key = relationship("ReportKey")
    question = relationship("Question")
