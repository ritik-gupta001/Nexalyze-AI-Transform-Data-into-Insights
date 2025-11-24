from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.schemas_tasks import TaskResponse, TaskStatus, SentimentSummary, TaskType
from app.core.logger import log
from app.genai.llm_client import LLMClient
from app.ml.sentiment_ml import SentimentMLModel
from app.ml.forecast_model import TrendForecastModel
from app.services.tools_news import NewsSearchTool
from app.services.tools_docs import DocumentProcessingTool
from app.services.tools_data import DataAnalysisTool
from app.services.tools_visualization import VisualizationTool
from app.services.tools_report import ReportGenerator
from app.db.models import Task


class TaskInterpreter:
    """Interprets natural language tasks into structured plans"""
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def interpret(self, query: str, entity: Optional[str] = None) -> Dict[str, Any]:
        """Interpret task from natural language"""
        return await self.llm_client.interpret_task(query)


class AgentOrchestrator:
    """
    Main agent that orchestrates task execution using various tools
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.llm = LLMClient()
        self.task_interpreter = TaskInterpreter()
        
        # Initialize tools
        self.news_tool = NewsSearchTool()
        self.doc_tool = DocumentProcessingTool()
        self.data_tool = DataAnalysisTool()
        self.viz_tool = VisualizationTool()
        self.report_gen = ReportGenerator()
        
        # Initialize models
        self.sentiment_model = SentimentMLModel()
        self.forecast_model = TrendForecastModel()
        
        log.info("AgentOrchestrator initialized")
    
    async def execute_text_analysis(
        self,
        task_id: str,
        query: str,
        entity: Optional[str] = None,
        time_range: Optional[str] = "last_7_days"
    ) -> TaskResponse:
        """Execute intelligent text/news analysis task"""
        
        # Save task to database
        task = Task(
            task_id=task_id,
            status=TaskStatus.PROCESSING.value,
            task_type=TaskType.NEWS_INSIGHT.value,
            query=query
        )
        self.db.add(task)
        self.db.commit()
        
        try:
            log.info(f"Starting intelligent text analysis for task {task_id}")
            
            # Step 1: Interpret task with enhanced understanding
            plan = await self.task_interpreter.interpret(query, entity)
            entity = entity or plan.get('entity', query[:50])  # Use query snippet if no entity
            user_intent = plan.get('user_intent', query)
            analysis_focus = plan.get('analysis_focus', 'comprehensive')
            time_range = plan.get('time_range', time_range)
            
            log.info(f"Analysis focus: {analysis_focus}, Entity: {entity}, Intent: {user_intent}")
            
            # Step 2: Search for contextually relevant news
            articles = await self.news_tool.search_news(entity, time_range)
            
            # Step 3: Analyze sentiment for each article
            sentiment_results = []
            for article in articles:
                sentiment = self.sentiment_model.predict(article['content'])
                sentiment_results.append(sentiment)
            
            # Step 4: Calculate overall sentiment
            if sentiment_results:
                avg_sentiment = {
                    'positive': sum(s['positive'] for s in sentiment_results) / len(sentiment_results),
                    'neutral': sum(s['neutral'] for s in sentiment_results) / len(sentiment_results),
                    'negative': sum(s['negative'] for s in sentiment_results) / len(sentiment_results)
                }
                overall_label = max(avg_sentiment, key=avg_sentiment.get)
                avg_sentiment['overall'] = overall_label
                avg_sentiment['confidence'] = avg_sentiment[overall_label]
            else:
                avg_sentiment = {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33, 
                               'overall': 'neutral', 'confidence': 0.34}
            
            # Step 5: Create visualizations
            charts = []
            
            # Sentiment chart
            sentiment_chart = await self.viz_tool.create_sentiment_chart(
                task_id, sentiment_results, entity
            )
            if sentiment_chart:
                charts.append(sentiment_chart)
            
            # Step 6: Forecast trend
            forecast_description = ""
            if len(sentiment_results) >= 3:
                forecast_description = self.forecast_model.forecast_sentiment(
                    sentiment_results, forecast_days=7
                )
                
                # Trend chart
                historical_scores = [s['positive'] for s in sentiment_results]
                forecast_scores, _ = self.forecast_model.predict_trend(historical_scores, 7)
                
                trend_chart = await self.viz_tool.create_trend_chart(
                    task_id, historical_scores, forecast_scores, entity
                )
                if trend_chart:
                    charts.append(trend_chart)
            
            # Step 7: Generate intelligent LLM analysis with context
            articles_text = self.news_tool.format_articles_for_analysis(articles)
            llm_analysis = await self.llm.analyze_news(
                entity=entity,
                articles=articles_text,
                intent=user_intent,
                focus=analysis_focus
            )
            
            # Step 8: Generate comprehensive contextual report
            sentiment_text = self.report_gen.format_sentiment_summary(avg_sentiment)
            
            report_content = await self.llm.generate_report(
                task_description=query,
                data_summary=llm_analysis,
                sentiment_data=sentiment_text,
                forecast_data=forecast_description,
                analysis_type=analysis_focus
            )
            
            # Step 9: Save report
            report_url = await self.report_gen.generate_pdf_report(
                task_id,
                f"Analysis Report: {entity}",
                report_content,
                charts
            )
            
            # Update task in database
            task.status = TaskStatus.COMPLETED.value
            task.summary = llm_analysis  # Full analysis, no truncation
            task.sentiment_summary = avg_sentiment
            task.forecast = forecast_description
            task.report_url = report_url
            task.charts = charts
            task.completed_at = datetime.utcnow()
            task.task_metadata = {
                'articles_analyzed': len(articles),
                'entity': entity,
                'time_range': time_range
            }
            self.db.commit()
            
            log.info(f"Task {task_id} completed successfully")
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                summary=llm_analysis,
                sentiment_summary=SentimentSummary(**avg_sentiment),
                forecast=forecast_description,
                report_url=report_url,
                charts=charts,
                metadata=task.task_metadata,
                created_at=task.created_at,
                completed_at=task.completed_at
            )
            
        except Exception as e:
            log.error(f"Error in text analysis: {e}")
            task.status = TaskStatus.FAILED.value
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def execute_document_analysis(
        self,
        task_id: str,
        file_content: bytes,
        filename: str,
        instruction: str
    ) -> TaskResponse:
        """Execute document analysis task without sentiment (not applicable to documents)"""
        
        task = Task(
            task_id=task_id,
            status=TaskStatus.PROCESSING.value,
            task_type=TaskType.DOCUMENT_ANALYSIS.value,
            instruction=instruction
        )
        self.db.add(task)
        self.db.commit()
        
        try:
            log.info(f"Starting document analysis for task {task_id}")
            
            # Step 1: Extract text from document
            text = await self.doc_tool.extract_text(file_content, filename)
            
            # Step 2: Extract sections (for research papers)
            sections = self.doc_tool.extract_sections(text)
            
            # Step 3: Get LLM analysis based on instruction
            analysis = await self.llm.analyze_document(filename, text[:4000], instruction)
            
            # Step 4: Generate summary
            summary = await self.llm.summarize(text[:3000], max_length=300)
            
            # Step 5: Generate report (NO SENTIMENT - not applicable for documents)
            report_content = f"""# Document Analysis: {filename}

## Instruction
{instruction}

## Summary
{summary}

## Detailed Analysis
{analysis}

## Document Statistics
- Total Length: {len(text):,} characters
- Estimated Words: {len(text.split()):,}
- Estimated Pages: {len(text) // 3000}
"""
            
            if sections:
                report_content += "\n## Document Structure\n"
                for section_name, section_content in sections.items():
                    report_content += f"\n### {section_name}\n{section_content[:200]}...\n"
            
            report_url = await self.report_gen.generate_pdf_report(
                task_id,
                f"Document Analysis: {filename}",
                report_content
            )
            
            # Update task (NO SENTIMENT_SUMMARY)
            task.status = TaskStatus.COMPLETED.value
            task.summary = analysis  # Full analysis, no truncation
            task.report_url = report_url
            task.completed_at = datetime.utcnow()
            task.task_metadata = {'filename': filename, 'text_length': len(text), 'word_count': len(text.split())}
            self.db.commit()
            
            log.info(f"Document task {task_id} completed")
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                summary=analysis,
                report_url=report_url,
                metadata=task.task_metadata,
                created_at=task.created_at,
                completed_at=task.completed_at
            )
            
        except Exception as e:
            log.error(f"Error in document analysis: {e}")
            task.status = TaskStatus.FAILED.value
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            self.db.commit()
            raise
    
    async def execute_data_analysis(
        self,
        task_id: str,
        file_content: bytes,
        filename: str,
        instruction: str
    ) -> TaskResponse:
        """Execute comprehensive CSV/Excel data analysis with trends and visualizations"""
        
        task = Task(
            task_id=task_id,
            status=TaskStatus.PROCESSING.value,
            task_type=TaskType.DATA_ANALYSIS.value,
            instruction=instruction
        )
        self.db.add(task)
        self.db.commit()
        
        try:
            log.info(f"Starting comprehensive data analysis for task {task_id}")
            
            # Step 1: Load data
            df = await self.data_tool.load_data(file_content, filename)
            
            # Step 2: Get comprehensive statistics
            stats = self.data_tool.get_statistics(df)
            stats_text = self.data_tool.format_stats_for_display(stats)
            
            # Step 3: Detect patterns and correlations
            patterns = self.data_tool.detect_patterns(df)
            
            # Step 4: Find anomalies
            anomalies = self.data_tool.find_anomalies(df)
            
            # Step 5: Get LLM insights
            sample_data = df.head(10).to_string()
            analysis = await self.llm.analyze_data(filename, stats_text, sample_data, instruction)
            
            # Step 6: Create comprehensive visualizations
            charts = []
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            # 6a. Distribution chart for first numeric column
            if len(numeric_cols) > 0:
                dist_chart = await self.viz_tool.create_distribution_chart(
                    task_id,
                    df[numeric_cols[0]].dropna().values,
                    f"Distribution: {numeric_cols[0]}"
                )
                if dist_chart:
                    charts.append(dist_chart)
            
            # 6b. Correlation heatmap if multiple numeric columns
            if len(numeric_cols) >= 2:
                corr_chart = await self.viz_tool.create_correlation_heatmap(
                    task_id,
                    df[numeric_cols].corr(),
                    "Correlation Matrix"
                )
                if corr_chart:
                    charts.append(corr_chart)
            
            # 6c. Time series / trend chart if there's a date column
            date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            if not date_cols:
                # Try to detect date columns
                for col in df.columns:
                    try:
                        import pandas as pd
                        df[col] = pd.to_datetime(df[col])
                        date_cols.append(col)
                        break
                    except:
                        pass
            
            if date_cols and len(numeric_cols) > 0:
                # Create trend chart
                trend_chart = await self.viz_tool.create_time_series_chart(
                    task_id,
                    df,
                    date_cols[0],
                    numeric_cols[0],
                    f"Trend: {numeric_cols[0]} over time"
                )
                if trend_chart:
                    charts.append(trend_chart)
            
            # 6d. Top correlations visualization
            if patterns['correlations']:
                top_corrs = patterns['correlations'][:5]
                corr_pairs = [f"{c['col1']}-{c['col2']}" for c in top_corrs]
                corr_values = [c['correlation'] for c in top_corrs]
                
                corr_bar_chart = await self.viz_tool.create_bar_chart(
                    task_id,
                    corr_pairs,
                    corr_values,
                    "Top Correlations"
                )
                if corr_bar_chart:
                    charts.append(corr_bar_chart)
            
            # Step 7: Generate comprehensive report with trends
            report_content = f"""# Data Analysis Report: {filename}

## Analysis Request
{instruction}

## Dataset Overview
{stats_text}

## Intelligent Analysis & Insights
{analysis}

## Patterns & Trends Detected
"""
            if patterns['correlations']:
                report_content += "\n### Strong Correlations Found:\n"
                for corr in patterns['correlations'][:5]:
                    strength = "Very Strong" if abs(corr['correlation']) > 0.8 else "Strong" if abs(corr['correlation']) > 0.6 else "Moderate"
                    direction = "Positive" if corr['correlation'] > 0 else "Negative"
                    report_content += f"- **{corr['col1']}** ↔ **{corr['col2']}**: {strength} {direction} correlation ({corr['correlation']:.3f})\n"
            
            if patterns['trends']:
                report_content += "\n### Trends Identified:\n"
                for trend in patterns['trends'][:5]:
                    report_content += f"- **{trend['column']}**: {trend['trend']}\n"
            
            if anomalies:
                report_content += "\n### Data Quality & Anomalies:\n"
                for anom in anomalies[:5]:
                    report_content += f"- **{anom['column']}**: {anom['count']} outliers detected ({anom.get('percentage', 0):.1f}% of data)\n"
            
            report_content += f"""\n## Visualizations Generated
{len(charts)} charts created for comprehensive analysis:
"""
            for i, chart in enumerate(charts, 1):
                report_content += f"{i}. {chart.split('/')[-1].replace('_', ' ').replace('.png', '')}\n"
            
            report_url = await self.report_gen.generate_pdf_report(
                task_id,
                f"Data Analysis: {filename}",
                report_content,
                charts
            )
            
            # Update task with all visualizations
            task.status = TaskStatus.COMPLETED.value
            task.summary = analysis  # Full analysis, no truncation
            task.report_url = report_url
            task.charts = charts
            task.completed_at = datetime.utcnow()
            task.task_metadata = {
                'filename': filename,
                'rows': stats['shape']['rows'],
                'columns': stats['shape']['columns'],
                'numeric_columns': len(numeric_cols),
                'correlations_found': len(patterns.get('correlations', [])),
                'charts_generated': len(charts)
            }
            self.db.commit()
            
            log.info(f"Data task {task_id} completed with {len(charts)} visualizations")
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                summary=analysis,
                report_url=report_url,
                charts=charts,
                metadata=task.task_metadata,
                created_at=task.created_at,
                completed_at=task.completed_at
            )
            
        except Exception as e:
            log.error(f"Error in data analysis: {e}")
            task.status = TaskStatus.FAILED.value
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            self.db.commit()
            raise
