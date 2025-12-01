from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional, List
from datetime import datetime
import uuid

from app.models.schemas_tasks import (
    TextAnalysisRequest,
    TaskResponse,
    TaskStatus,
    TaskListResponse
)
from app.services.agent_orchestrator import AgentOrchestrator
from app.core.logger import log
from app.db.base import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/analyze-text", response_model=TaskResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze text/news with sentiment analysis and trend forecasting
    
    Example:
    ```json
    {
        "query": "Analyze recent news about Tesla and predict sentiment trend",
        "entity": "Tesla",
        "time_range": "last_7_days"
    }
    ```
    """
    try:
        log.info(f"Received text analysis request: {request.query}")
        
        # Create task ID
        task_id = f"T-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(db=db)
        
        # Execute task
        result = await orchestrator.execute_text_analysis(
            task_id=task_id,
            query=request.query,
            entity=request.entity,
            time_range=request.time_range
        )
        
        log.info(f"Task {task_id} completed successfully")
        return result
        
    except Exception as e:
        log.error(f"Error in text analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-doc", response_model=TaskResponse)
async def analyze_document(
    file: UploadFile = File(...),
    instruction: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded PDF/DOCX document
    
    Upload a document and provide instructions like:
    - "Summarize key findings and limitations"
    - "Extract methodology and results"
    - "Identify main conclusions"
    """
    try:
        log.info(f"Received document analysis: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {allowed_extensions}"
            )
        
        # Create task ID
        task_id = f"T-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Read file content
        content = await file.read()
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(db=db)
        
        # Execute task
        result = await orchestrator.execute_document_analysis(
            task_id=task_id,
            file_content=content,
            filename=file.filename,
            instruction=instruction or "Analyze and extract key insights from this document"
        )
        
        log.info(f"Document task {task_id} completed")
        return result
        
    except Exception as e:
        log.error(f"Error in document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-data", response_model=TaskResponse)
async def analyze_data(
    file: UploadFile = File(...),
    instruction: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Analyze CSV/Excel data files
    
    Upload data and ask questions like:
    - "Find patterns and anomalies"
    - "Predict sales trends for next quarter"
    - "Identify key factors affecting performance"
    """
    try:
        log.info(f"Received data analysis: {file.filename}")
        
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        if not any(file.filename.endswith(ext) for ext in allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {allowed_extensions}"
            )
        
        # Create task ID
        task_id = f"T-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}"
        
        # Read file content
        content = await file.read()
        
        # Initialize agent orchestrator
        orchestrator = AgentOrchestrator(db=db)
        
        # Execute task
        result = await orchestrator.execute_data_analysis(
            task_id=task_id,
            file_content=content,
            filename=file.filename,
            instruction=instruction or "Analyze this data, find patterns, trends, and provide insights"
        )
        
        log.info(f"Data task {task_id} completed")
        return result
        
    except Exception as e:
        log.error(f"Error in data analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get status and results of a specific task
    """
    try:
        from app.db.models import Task
        
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            task_id=task.task_id,
            status=TaskStatus(task.status),
            summary=task.summary or "",
            sentiment_summary=task.sentiment_summary,
            forecast=task.forecast,
            report_url=task.report_url,
            charts=task.charts or [],
            metadata=task.task_metadata or {},
            created_at=task.created_at,
            completed_at=task.completed_at,
            error=task.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error fetching task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    page: int = 1,
    page_size: int = 10,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """
    List all tasks with pagination and optional filtering
    """
    try:
        from app.db.models import Task
        
        query = db.query(Task)
        
        if status:
            query = query.filter(Task.status == status.value)
        
        total = query.count()
        
        tasks = query.order_by(Task.created_at.desc()).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        task_responses = [
            TaskResponse(
                task_id=task.task_id,
                status=TaskStatus(task.status),
                summary=task.summary or "",
                sentiment_summary=task.sentiment_summary,
                forecast=task.forecast,
                report_url=task.report_url,
                charts=task.charts or [],
                metadata=task.task_metadata or {},
                created_at=task.created_at,
                completed_at=task.completed_at,
                error=task.error
            )
            for task in tasks
        ]
        
        return TaskListResponse(
            tasks=task_responses,
            total=total,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        log.error(f"Error listing tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
