from typing import List, Dict, Any
import re
from datetime import datetime, timedelta
import random

from app.core.logger import log


class NewsSearchTool:
    """Tool for searching and fetching news articles"""
    
    def __init__(self):
        self.api_key = None  # Can integrate with NewsAPI or similar
    
    async def search_news(
        self,
        entity: str,
        time_range: str = "last_7_days",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles about an entity
        
        For demo purposes, returns mock data.
        In production, integrate with NewsAPI, Google News, or web scraping.
        """
        try:
            log.info(f"Searching news for: {entity}")
            
            # Parse time range
            days = self._parse_time_range(time_range)
            
            # Mock news data (replace with real API calls)
            mock_articles = self._generate_mock_news(entity, days, max_results)
            
            log.info(f"Found {len(mock_articles)} articles")
            return mock_articles
            
        except Exception as e:
            log.error(f"Error searching news: {e}")
            return []
    
    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to days"""
        match = re.search(r'(\d+)', time_range)
        if match:
            return int(match.group(1))
        return 7  # Default
    
    def _generate_mock_news(self, entity: str, days: int, count: int) -> List[Dict[str, Any]]:
        """Generate query-specific dynamic news articles"""
        import random
        
        # Detect query type and generate relevant content
        entity_lower = entity.lower()
        
        # City/Location-specific news
        if any(city in entity_lower for city in ['delhi', 'mumbai', 'bangalore', 'chennai', 'kolkata', 'hyderabad', 'pune', 'ahmedabad']):
            city_name = entity.split()[0] if ' ' in entity else entity
            templates = [
                {
                    "title": f"{city_name} Metro Expansion Project Reaches Major Milestone",
                    "content": f"The {city_name} Metro Rail Corporation announced today that the new metro line extension has reached a significant construction milestone. The project, valued at over ₹15,000 crores, is expected to ease traffic congestion and provide sustainable transport options for millions of commuters. Officials stated the line will be operational by Q3 2026, connecting key commercial and residential areas across the city."
                },
                {
                    "title": f"{city_name} Emerges as Leading Tech Hub with Record Startup Funding",
                    "content": f"In a significant development for the city's tech ecosystem, {city_name} has witnessed record startup investments in 2025. According to recent reports, the city attracted over $2.5 billion in venture capital funding across 450+ startups. Industry leaders attribute this growth to improved infrastructure, skilled talent pool, and supportive government policies promoting innovation and entrepreneurship."
                },
                {
                    "title": f"Air Quality Concerns Prompt {city_name} Government to Launch Clean Air Initiative",
                    "content": f"Responding to growing environmental concerns, the {city_name} municipal authority has unveiled a comprehensive clean air action plan. The initiative includes restrictions on older vehicles, increased green cover, and promotion of electric vehicles. Environmental experts have welcomed the move, though some suggest more aggressive measures may be needed to achieve WHO air quality standards."
                },
                {
                    "title": f"{city_name} Real Estate Market Shows Mixed Signals Amid Economic Shifts",
                    "content": f"The {city_name} property market is experiencing diverse trends across different segments. While premium residential areas have seen price appreciation of 8-12%, mid-range segments remain stable. Commercial real estate, particularly office spaces, faces challenges due to hybrid work models. Real estate analysts suggest the market is in a transitional phase adapting to post-pandemic realities."
                },
                {
                    "title": f"Major Infrastructure Project Announced: {city_name} to Get New International Convention Center",
                    "content": f"The government has approved a state-of-the-art international convention center for {city_name}, designed to boost business tourism and position the city as a global MICE destination. The ₹2,800 crore facility will feature world-class amenities and is expected to generate thousands of jobs while contributing significantly to the local economy through increased tourism and business events."
                },
                {
                    "title": f"{city_name} Schools Adopt AI-Powered Learning Tools in Education Revolution",
                    "content": f"Educational institutions across {city_name} are embracing artificial intelligence and adaptive learning technologies to enhance student outcomes. Over 200 schools have implemented AI-based personalized learning platforms, marking a significant shift in pedagogy. Educators report improved student engagement and learning outcomes, though concerns about digital divide and screen time persist among parent groups."
                },
                {
                    "title": f"Traffic Congestion Crisis: {city_name} Explores Smart Mobility Solutions",
                    "content": f"With traffic congestion costing the city an estimated ₹1,500 crores annually in lost productivity, {city_name} authorities are piloting smart traffic management systems powered by AI and IoT sensors. The initiative includes intelligent signal control, real-time traffic monitoring, and integrated public transport apps. Early results from pilot zones show 20-25% improvement in traffic flow during peak hours."
                },
                {
                    "title": f"{city_name} Healthcare Sector Sees Surge in Medical Tourism Revenue",
                    "content": f"Premium hospitals in {city_name} reported a 40% increase in international patient arrivals, establishing the city as a leading medical tourism destination. Specialties including cardiac care, orthopedics, and cosmetic surgery are attracting patients from across the globe. The sector's growth is attributed to world-class facilities, skilled doctors, and cost-effectiveness compared to Western countries."
                },
                {
                    "title": f"Cultural Revival: {city_name} Heritage Sites Get Modern Makeover",
                    "content": f"In an effort to preserve history while embracing modernity, {city_name}'s heritage sites are undergoing restoration with state-of-the-art conservation techniques. The ₹500 crore project includes improved visitor facilities, digital guides, and enhanced security. Tourism department officials expect visitor numbers to increase by 60% post-restoration, boosting local economy and cultural awareness."
                },
                {
                    "title": f"{city_name} Grapples with Water Scarcity: New Reservoirs Planned",
                    "content": f"Addressing critical water supply concerns, the {city_name} water board has proposed construction of three new reservoirs and rainwater harvesting infrastructure across the city. The ₹3,200 crore project aims to ensure water security for the growing population. However, environmentalists have raised concerns about ecological impact and called for emphasis on water conservation and recycling initiatives."
                }
            ]
        
        # Tech/AI/Industry news
        elif any(tech in entity_lower for tech in ['ai', 'artificial intelligence', 'tech', 'technology', 'startup', 'software']):
            templates = [
                {
                    "title": f"{entity}: Breakthrough AI Model Achieves Human-Level Performance in Complex Tasks",
                    "content": f"Researchers in the {entity} sector have unveiled a revolutionary AI system demonstrating unprecedented capabilities. The model shows remarkable proficiency in reasoning, creativity, and problem-solving, potentially transforming industries from healthcare to finance. Experts suggest this represents a significant leap forward, though ethical considerations and regulatory frameworks remain subjects of intense debate."
                },
                {
                    "title": f"Major Investment Wave: {entity} Sector Attracts Record Funding",
                    "content": f"The {entity} industry experienced its strongest quarter with $8.5 billion in investments across 300+ companies. Leading venture capital firms cite explosive growth potential and transformative applications driving funding decisions. However, analysts warn about market saturation and emphasize importance of sustainable business models over hype-driven valuations."
                },
                {
                    "title": f"{entity} Faces Regulatory Scrutiny Over Data Privacy and Ethics",
                    "content": f"Government authorities have launched investigations into {entity} practices regarding user data protection and algorithmic transparency. The probe follows widespread concerns about privacy violations and biased decision-making systems. Industry leaders call for balanced regulation that protects consumers while fostering innovation and technological advancement."
                }
            ]
        
        # Stock/Finance/Company news
        elif any(fin in entity_lower for fin in ['stock', 'market', 'finance', 'investment', 'trading']):
            templates = [
                {
                    "title": f"{entity} Reaches All-Time High Amid Strong Quarterly Results",
                    "content": f"Markets responded enthusiastically as {entity} reported exceptional quarterly performance, with revenues up 28% year-over-year. The company exceeded analyst expectations across all key metrics, driving share prices to historic levels. Management attributed success to strategic initiatives, operational excellence, and favorable market conditions, while announcing plans for continued expansion."
                },
                {
                    "title": f"Volatility Concerns: {entity} Experiences Correction After Sustained Rally",
                    "content": f"After months of strong performance, {entity} faced a sharp correction as profit-taking and macroeconomic concerns weighed on investor sentiment. Analysts suggest the pullback is healthy consolidation rather than trend reversal, citing strong fundamentals. However, technical indicators show mixed signals, prompting cautious approach among institutional investors."
                },
                {
                    "title": f"{entity} Analyst Consensus Shifts to Bullish on Growth Prospects",
                    "content": f"Leading financial institutions have upgraded their outlook on {entity}, citing improved market positioning and execution capability. The revised forecasts project 35-40% growth over next 18 months, supported by new product launches and market expansion. However, some analysts maintain reservations about valuation levels and competitive pressures in the sector."
                }
            ]
        
        # Default: General news
        else:
            templates = [
                {
                    "title": f"{entity} Announces Major Strategic Initiative for 2025-26",
                    "content": f"In a significant development, {entity} has unveiled an ambitious strategic plan focusing on innovation, sustainability, and market expansion. The initiative involves substantial investments in research, technology, and talent acquisition. Industry experts suggest this positions {entity} favorably for future growth, though execution will be critical to realizing stated objectives."
                },
                {
                    "title": f"Expert Analysis: What's Next for {entity} in Evolving Landscape",
                    "content": f"Industry analysts are closely examining {entity}'s trajectory amid rapidly changing market dynamics. While opportunities for growth and innovation abound, challenges including regulatory changes, competitive pressures, and technological disruption require strategic navigation. Thought leaders emphasize importance of adaptability and forward-thinking leadership in current environment."
                },
                {
                    "title": f"{entity} Launches Sustainability Program Addressing Climate Concerns",
                    "content": f"Responding to growing environmental awareness, {entity} has committed to comprehensive sustainability initiatives including carbon neutrality targets and renewable energy adoption. The program has received positive reception from environmental groups, though some critics argue for more aggressive timelines and measurable accountability mechanisms to ensure meaningful environmental impact."
                }
            ]
        
        # Randomize and create articles
        random.shuffle(templates)
        selected = templates[:min(count, len(templates))]
        
        articles = []
        for i, template in enumerate(selected):
            date = datetime.now() - timedelta(days=random.randint(0, days))
            
            article = {
                "title": template["title"],
                "content": template["content"],
                "source": random.choice(["The Times", "Business Standard", "Economic Times", "Hindustan Times", "Indian Express", "Mint", "Reuters India", "PTI"]),
                "published_at": date.isoformat(),
                "url": f"https://example.com/news-{i}",
                "sentiment_hint": "neutral"
            }
            articles.append(article)
        
        return articles
    
    def format_articles_for_analysis(self, articles: List[Dict]) -> str:
        """Format articles into text for LLM analysis"""
        formatted = []
        
        for i, article in enumerate(articles, 1):
            formatted.append(f"Article {i}:")
            formatted.append(f"Title: {article['title']}")
            formatted.append(f"Source: {article['source']}")
            formatted.append(f"Date: {article['published_at'][:10]}")
            formatted.append(f"Content: {article['content'][:300]}...")
            formatted.append("")
        
        return "\n".join(formatted)
