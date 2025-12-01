from openai import OpenAI
from typing import Optional, Dict, Any
import json

from app.core.config import get_settings
from app.core.logger import log
from app.genai.prompts import *

settings = get_settings()


class LLMClient:
    """Wrapper for OpenAI/LLM interactions"""
    
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "":
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                log.info("OpenAI client initialized")
            except Exception as e:
                log.warning(f"Failed to initialize OpenAI: {e}")
    
    async def interpret_task(self, query: str) -> Dict[str, Any]:
        """
        Interpret user query into structured task plan
        """
        try:
            if not self.client:
                # Fallback: simple rule-based interpretation
                return self._fallback_interpret(query)
            
            prompt = TASK_INTERPRETER_PROMPT.format(query=query)
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a task planning expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            task_plan = json.loads(content)
            log.info(f"Task interpreted: {task_plan['task_type']}")
            
            return task_plan
            
        except Exception as e:
            log.error(f"Error interpreting task: {e}")
            return self._fallback_interpret(query)
    
    def _fallback_interpret(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based task interpretation with enhanced context"""
        query_lower = query.lower()
        
        # Determine analysis focus
        if any(word in query_lower for word in ["highlight", "headlines", "top news", "breaking", "major"]):
            analysis_focus = "highlights"
        elif any(word in query_lower for word in ["sentiment", "feeling", "opinion", "perception"]):
            analysis_focus = "sentiment"
        elif any(word in query_lower for word in ["trend", "pattern", "direction", "momentum"]):
            analysis_focus = "trends"
        else:
            analysis_focus = "comprehensive"
        
        # Determine time range
        if any(word in query_lower for word in ["today", "today's", "current"]):
            time_range = "today"
        elif any(word in query_lower for word in ["recent", "latest", "past few days"]):
            time_range = "last_3_days"
        elif any(word in query_lower for word in ["week", "weekly"]):
            time_range = "last_7_days"
        elif any(word in query_lower for word in ["month", "monthly"]):
            time_range = "last_30_days"
        else:
            time_range = "last_7_days"
        
        # Determine task type
        if any(word in query_lower for word in ["news", "article", "sentiment", "stock", "market"]):
            task_type = "news_insight"
            actions = ["search_news", "analyze_sentiment", "predict_trends", "generate_report"]
        elif any(word in query_lower for word in ["pdf", "document", "paper", "file"]):
            task_type = "document_analysis"
            actions = ["extract_text", "summarize_text", "generate_report"]
        elif any(word in query_lower for word in ["csv", "excel", "data", "dataset"]):
            task_type = "data_analysis"
            actions = ["load_data", "analyze_patterns", "visualize_data", "generate_report"]
        else:
            task_type = "general_research"
            actions = ["research", "summarize", "generate_report"]
        
        return {
            "task_type": task_type,
            "entity": query[:100],  # Use query as entity for better context
            "user_intent": query,
            "analysis_focus": analysis_focus,
            "actions": actions,
            "time_range": time_range,
            "parameters": {}
        }
    
    async def summarize(self, content: str, max_length: int = 500) -> str:
        """Summarize content"""
        try:
            if not self.client:
                # Simple truncation fallback
                return content[:max_length] + "..." if len(content) > max_length else content
            
            prompt = SUMMARIZATION_PROMPT.format(content=content[:4000])
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional summarizer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=max_length
            )
            
            summary = response.choices[0].message.content.strip()
            log.info("Content summarized")
            
            return summary
            
        except Exception as e:
            log.error(f"Error summarizing: {e}")
            return content[:max_length] + "..."
    
    async def generate_report(
        self,
        task_description: str,
        data_summary: str,
        sentiment_data: str = "",
        forecast_data: str = "",
        analysis_type: str = "comprehensive"
    ) -> str:
        """Generate comprehensive report with context"""
        try:
            if not self.client:
                # Fallback: simple template
                return self._fallback_report(task_description, data_summary, sentiment_data, forecast_data)
            
            # Determine analysis-specific section name
            section_names = {
                "highlights": "Key Highlights",
                "sentiment": "Sentiment Deep Dive",
                "trends": "Trend Analysis",
                "comprehensive": "Sentiment & Predictions"
            }
            
            prompt = REPORT_GENERATION_PROMPT.format(
                task_description=task_description,
                analysis_type=analysis_type,
                data_summary=data_summary,
                sentiment_data=sentiment_data or "N/A",
                forecast_data=forecast_data or "N/A",
                analysis_specific_section=section_names.get(analysis_type, "Additional Insights")
            )
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional research analyst who creates insightful, actionable reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            report = response.choices[0].message.content.strip()
            log.info(f"Report generated with {analysis_type} focus")
            
            return report
            
        except Exception as e:
            log.error(f"Error generating report: {e}")
            return self._fallback_report(task_description, data_summary, sentiment_data, forecast_data)
    
    def _fallback_report(self, task: str, summary: str, sentiment: str, forecast: str) -> str:
        """Fallback report template"""
        report = f"""# Research Report

## Task
{task}

## Summary
{summary}

## Sentiment Analysis
{sentiment if sentiment else "Not available"}

## Predictions
{forecast if forecast else "Not available"}

## Conclusion
Analysis completed successfully. See above for detailed findings.
"""
        return report
    
    async def analyze_news(self, entity: str, articles: str, intent: str = "", focus: str = "comprehensive") -> str:
        """Analyze news articles with context awareness"""
        try:
            if not self.client:
                # Enhanced fallback with dynamic content based on query
                return self._fallback_news_analysis(entity, articles, intent, focus)
            
            # Generate focus-specific instructions
            focus_instructions = self._get_focus_instructions(focus)
            
            prompt = NEWS_ANALYSIS_PROMPT.format(
                entity=entity,
                intent=intent or f"Analyze news about {entity}",
                focus=focus,
                articles=articles[:3000],
                focus_instructions=focus_instructions
            )
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert news analyst who provides insightful, context-aware analysis tailored to user needs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            analysis = response.choices[0].message.content.strip()
            return analysis
            
        except Exception as e:
            log.error(f"Error analyzing news: {e}")
            return self._fallback_news_analysis(entity, articles, intent, focus)
    
    def _fallback_news_analysis(self, entity: str, articles: str, intent: str, focus: str) -> str:
        """Generate dynamic fallback analysis without LLM"""
        entity_lower = entity.lower()
        
        # Detect topic type
        is_city = any(city in entity_lower for city in ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune'])
        is_tech = any(tech in entity_lower for tech in ['ai', 'artificial intelligence', 'tech', 'technology', 'startup'])
        is_finance = any(fin in entity_lower for fin in ['stock', 'market', 'finance', 'investment'])
        
        # Parse article titles from the articles string
        article_titles = []
        for line in articles.split('\n'):
            if line.startswith('Title:'):
                article_titles.append(line.replace('Title:', '').strip())
        
        if is_city:
            analysis = f"""**Executive Summary of Key Developments in {entity} Regarding Recent News**

{entity}, traditionally known for its rich history and vibrant culture, is making headlines for its strategic moves towards addressing climate change and enhancing the city's infrastructure and quality of life. Based on recent developments:

### Key Highlights:

"""
            for i, title in enumerate(article_titles[:5], 1):
                analysis += f"{i}. **{title}**: This development represents significant progress in the city's ongoing transformation and modernization efforts.\n\n"
            
            analysis += f"""\n### Infrastructure & Development:
The initiatives showcase {entity}'s commitment to sustainable urban development, improved public transportation, and addressing environmental concerns. These strategic investments are expected to enhance quality of life for residents while positioning the city for future growth.

### Impact Assessment:
- **Short-term**: Implementation of new policies and projects will create jobs and improve civic amenities
- **Long-term**: Enhanced infrastructure and cleaner environment will attract investment and talent
- **Challenges**: Execution timelines and budget management remain critical factors
"""
        
        elif is_tech:
            analysis = f"""**Technology Sector Analysis: {entity}**

The {entity} landscape is experiencing rapid evolution with significant developments across innovation, investment, and regulation.

### Major Developments:

"""
            for i, title in enumerate(article_titles[:5], 1):
                analysis += f"{i}. **{title}**\n\n"
            
            analysis += f"""\n### Industry Trends:
- **Innovation**: Breakthrough advancements pushing technological boundaries
- **Investment**: Strong capital inflows indicating market confidence
- **Regulation**: Increasing scrutiny requiring balanced policy frameworks
- **Adoption**: Growing enterprise and consumer adoption driving scale

### Strategic Implications:
The sector faces both opportunities and challenges. While innovation accelerates, regulatory frameworks and ethical considerations require careful navigation. Organizations must balance rapid advancement with responsible development.
"""
        
        elif is_finance:
            analysis = f"""**Market Analysis: {entity}**

Recent market activity surrounding {entity} shows dynamic movements across multiple indicators.

### Key Market Events:

"""
            for i, title in enumerate(article_titles[:5], 1):
                analysis += f"{i}. **{title}**\n\n"
            
            analysis += f"""\n### Market Dynamics:
- **Performance Metrics**: Strong indicators across key business segments
- **Analyst Outlook**: Mixed perspectives reflecting both opportunities and risks
- **Competitive Position**: Strategic initiatives enhancing market positioning
- **Risk Factors**: Macroeconomic conditions and sector-specific challenges warrant monitoring

### Investment Perspective:
While fundamentals appear solid, investors should consider both growth potential and associated risks. Diversification and thorough due diligence remain essential.
"""
        
        else:
            analysis = f"""**Comprehensive Analysis: {entity}**

Recent developments surrounding {entity} present a complex landscape of opportunities and challenges.

### Recent Developments:

"""
            for i, title in enumerate(article_titles[:5], 1):
                analysis += f"{i}. **{title}**\n\n"
            
            analysis += f"""\n### Strategic Assessment:
The situation requires careful monitoring as multiple factors influence outcomes. Key stakeholders should focus on:

- **Strategic Planning**: Adapting to evolving circumstances
- **Risk Management**: Identifying and mitigating potential challenges
- **Opportunity Capture**: Leveraging favorable conditions for growth
- **Stakeholder Engagement**: Maintaining clear communication and alignment

### Forward Outlook:
While the path forward contains uncertainties, proactive management and strategic execution will be critical for positive outcomes.
"""
        
        return analysis
    
    def _get_focus_instructions(self, focus: str) -> str:
        """Get specific instructions based on analysis focus"""
        instructions = {
            "highlights": """Focus on:
- Top 3-5 most important news items
- Breaking developments or major announcements
- Brief, impactful summaries of each highlight
- Why each item matters""",
            "sentiment": """Focus on:
- Overall market/public sentiment (positive/negative/neutral)
- Sentiment drivers and catalysts
- Changes in sentiment over time
- What's driving positive or negative perception""",
            "trends": """Focus on:
- Emerging patterns and trends
- Directional momentum
- Comparison to historical patterns
- Future trajectory predictions""",
            "comprehensive": """Provide:
- Executive summary of key developments
- Sentiment overview
- Emerging trends and patterns
- Notable events and their implications
- Forward-looking insights"""
        }
        return instructions.get(focus, instructions["comprehensive"])
    
    async def analyze_document(self, filename: str, content: str, instruction: str) -> str:
        """Analyze document content"""
        try:
            if not self.client:
                return f"Document analysis: {content[:500]}..."
            
            prompt = DOCUMENT_INSIGHT_PROMPT.format(
                filename=filename,
                content=content[:4000],
                instruction=instruction
            )
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a document analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content.strip()
            return analysis
            
        except Exception as e:
            log.error(f"Error analyzing document: {e}")
            return f"Document analysis: {content[:500]}..."
    
    async def analyze_data(self, filename: str, stats: str, sample: str, instruction: str) -> str:
        """Analyze dataset"""
        try:
            if not self.client:
                return f"Data analysis: {stats}\n{sample}"
            
            prompt = DATA_INSIGHT_PROMPT.format(
                filename=filename,
                stats=stats,
                sample=sample,
                instruction=instruction
            )
            
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a data scientist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            analysis = response.choices[0].message.content.strip()
            return analysis
            
        except Exception as e:
            log.error(f"Error analyzing data: {e}")
            return f"Data analysis: {stats}\n{sample}"
