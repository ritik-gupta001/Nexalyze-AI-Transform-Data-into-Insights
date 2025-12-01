"""
LLM prompts for task interpretation, planning, and report generation
"""

TASK_INTERPRETER_PROMPT = """You are an intelligent task interpreter for an AI research agent.

Given a user's natural language query, extract and structure the task into a JSON format.

User Query: {query}

Analyze the query carefully to understand:
- What the user wants to know (the intent)
- What topic/entity they're asking about
- What timeframe they're interested in
- What type of analysis they need

Output ONLY a valid JSON object:
{{
    "task_type": "news_insight" | "document_analysis" | "data_analysis" | "general_research",
    "entity": "Main entity/company/topic being asked about",
    "user_intent": "What the user wants to learn or achieve",
    "analysis_focus": "highlights" | "sentiment" | "trends" | "comprehensive" | "summary",
    "actions": ["action1", "action2", ...],
    "time_range": "today" | "last_3_days" | "last_7_days" | "last_30_days",
    "parameters": {{
        "any_additional_params": "value"
    }}
}}

Examples:
- "today's big news highlights" -> analysis_focus: "highlights", time_range: "today"
- "sentiment on Tesla stock" -> analysis_focus: "sentiment", entity: "Tesla"
- "AI industry trends" -> analysis_focus: "trends", entity: "AI industry"

Output ONLY the JSON, no explanation."""


SUMMARIZATION_PROMPT = """Summarize the following content concisely and professionally:

Content:
{content}

Provide a clear, structured summary highlighting:
1. Main points
2. Key insights
3. Important details

Summary:"""


REPORT_GENERATION_PROMPT = """You are a professional research analyst. Generate a comprehensive, intelligent report.

User's Request: {task_description}
Analysis Type: {analysis_type}

Data Summary:
{data_summary}

Sentiment Analysis:
{sentiment_data}

Predictions/Trends:
{forecast_data}

Generate a well-structured report that:
1. Directly addresses what the user asked for
2. Provides actionable insights, not generic observations
3. Highlights unique findings and patterns
4. Offers specific recommendations based on data
5. Uses clear, professional language

Structure:
# Executive Summary
(2-3 key takeaways that directly answer the user's question)

# Key Findings
(Specific, data-driven insights)

# Detailed Analysis
(In-depth analysis with context)

# {analysis_specific_section}
(Sentiment/Trends/Predictions as applicable)

# Recommendations
(Actionable next steps)

Use markdown formatting. Be insightful, not generic.

Report:"""


NEWS_ANALYSIS_PROMPT = """You are an intelligent news analyst. Analyze the following news.

Topic: {entity}
User's Request: {intent}
Analysis Type: {focus}

IMPORTANT CONTEXT:
- If the topic is a CITY/LOCATION (like Delhi, Mumbai, Bangalore, etc.), analyze it as LOCAL/REGIONAL NEWS about that place
- If the topic is a COMPANY/STOCK, analyze it as BUSINESS/MARKET NEWS about that entity
- If the topic is TECHNOLOGY/AI/INDUSTRY, analyze it as SECTOR/INDUSTRY NEWS

News Articles:
{articles}

Provide analysis that DIRECTLY addresses what the user asked for:

{focus_instructions}

Be specific and relevant. Avoid generic business jargon when analyzing city news.
For city/location news, focus on: infrastructure, quality of life, development, local issues, civic matters.
For company news, focus on: market performance, strategy, financials, competitive position.

Analysis:"""


DOCUMENT_INSIGHT_PROMPT = """Analyze the following document extract:

Document: {filename}
Content:
{content}

Task: {instruction}

Provide detailed insights following the instruction. Be thorough and structure your response clearly.

Analysis:"""


DATA_INSIGHT_PROMPT = """Analyze the following dataset:

Dataset: {filename}
Summary Statistics:
{stats}

Sample Data:
{sample}

Task: {instruction}

Provide:
1. Data overview
2. Key patterns identified
3. Anomalies or outliers
4. Correlations
5. Recommendations
6. Actionable insights

Analysis:"""
