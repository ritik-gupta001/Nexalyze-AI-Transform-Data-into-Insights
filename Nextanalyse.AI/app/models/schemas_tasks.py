from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    """Type of task to execute"""
    NEWS_INSIGHT = "news_insight"
    DOCUMENT_ANALYSIS = "document_analysis"
    DATA_ANALYSIS = "data_analysis"
    GENERAL_RESEARCH = "general_research"


class TextAnalysisRequest(BaseModel):
    """Request for text/news analysis"""
    query: str = Field(..., description="Natural language query for analysis")
    entity: Optional[str] = Field(None, description="Entity to focus on (e.g., company name)")
    time_range: Optional[str] = Field("last_7_days", description="Time range for data")


class DocumentAnalysisRequest(BaseModel):
    """Request for document analysis"""
    instruction: str = Field(..., description="What to do with the document")


class DataAnalysisRequest(BaseModel):
    """Request for CSV/Excel data analysis"""
    instruction: str = Field(..., description="What insights to extract")


class SentimentSummary(BaseModel):
    """Sentiment analysis summary"""
    positive: float = Field(..., ge=0, le=1)
    neutral: float = Field(..., ge=0, le=1)
    negative: float = Field(..., ge=0, le=1)
    overall: str = Field(..., description="Overall sentiment label")
    confidence: float = Field(..., ge=0, le=1)


class TaskPlan(BaseModel):
    """Structured task execution plan"""
    task_type: TaskType
    entity: Optional[str] = None
    actions: List[str] = Field(default_factory=list)
    time_range: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response for a completed task"""
    task_id: str
    status: TaskStatus
    summary: str
    sentiment_summary: Optional[SentimentSummary] = None
    forecast: Optional[str] = None
    report_url: Optional[str] = None
    charts: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class TaskListResponse(BaseModel):
    """List of tasks"""
    tasks: List[TaskResponse]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    timestamp: datetime
