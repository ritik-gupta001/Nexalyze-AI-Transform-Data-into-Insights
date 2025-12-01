from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.db.base import Base


class Task(Base):
    """Task database model"""
    __tablename__ = "tasks"
    
    task_id = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, default="pending")
    task_type = Column(String, nullable=False)
    
    # Query/instruction
    query = Column(Text, nullable=True)
    instruction = Column(Text, nullable=True)
    
    # Results
    summary = Column(Text, nullable=True)
    sentiment_summary = Column(JSON, nullable=True)
    forecast = Column(Text, nullable=True)
    
    # Files
    report_url = Column(String, nullable=True)
    charts = Column(JSON, nullable=True)  # List of chart URLs
    
    # Metadata
    task_metadata = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Task {self.task_id} - {self.status}>"


class Report(Base):
    """Report database model"""
    __tablename__ = "reports"
    
    report_id = Column(String, primary_key=True, index=True)
    task_id = Column(String, nullable=False, index=True)
    
    # Report content
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    format = Column(String, nullable=False)  # pdf, markdown, docx
    
    # File path
    file_path = Column(String, nullable=False)
    
    # Metadata
    report_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Report {self.report_id} for Task {self.task_id}>"
