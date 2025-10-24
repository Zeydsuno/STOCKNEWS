import json
import logging
from typing import Dict, List, Optional
from app.analysis.glm_client import GLMClient
from config import LARGE_CAP_STOCKS, MIN_IMPACT_SCORE

logger = logging.getLogger(__name__)

class NewsImpactAnalyzer:
    """Analyze news impact using GLM"""

    def __init__(self):
        self.glm_client = GLMClient()

    def analyze_single_article(self, article: Dict) -> Optional[Dict]:
        """Analyze impact of a single news article"""
        try:
            # Prepare the analysis prompt
            prompt = self._build_analysis_prompt(article)

            # Call GLM for analysis
            response = self.glm_client.call_glm(prompt, temperature=0.1)

            # Parse the JSON response
            analysis = self._parse_analysis_response(response, article)

            if analysis and analysis.get('impact_score', 0) >= MIN_IMPACT_SCORE:
                return analysis
            else:
                return None

        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None

    def analyze_multiple_articles(self, articles: List[Dict]) -> List[Dict]:
        """Analyze multiple articles and filter by impact score"""
        analyzed_articles = []

        for i, article in enumerate(articles):
            logger.info(f"Analyzing article {i+1}/{len(articles)}: {article.get('title', 'Unknown')[:50]}...")

            analysis = self.analyze_single_article(article)
            if analysis:
                analyzed_articles.append(analysis)
                logger.info(f"  ✅ Impact Score: {analysis.get('impact_score', 0)}")
            else:
                logger.info(f"  ❌ Low impact or analysis failed")

        return analyzed_articles

    def _build_analysis_prompt(self, article: Dict) -> str:
        """Build prompt for GLM analysis"""
        title = article.get('title', '')
        description = article.get('description', '')
        source = article.get('source', 'Unknown')
        content = article.get('content', '')

        # Limit content length to avoid token limits
        if len(content) > 500:
            content = content[:500] + "..."

        prompt = f"""
Analyze this financial news for US stock market impact:

HEADLINE: {title}
SUMMARY: {description}
SOURCE: {source}
FULL CONTENT: {content}

Task: Analyze market impact and provide structured analysis.

Please provide the analysis as JSON in this exact format:
{{
    "tickers": ["TICKER1", "TICKER2"],
    "impact_score": 8,
    "price_impact": "positive",
    "category": "earnings|m&a|tech-ai|macro|trading",
    "reasoning": "Brief explanation of impact reasoning",
    "market_significance": "high|medium|low"
}}

Analysis Guidelines:
1. Ticker Extraction: Find all stock tickers mentioned (prioritize: {', '.join(LARGE_CAP_STOCKS[:10])})
2. Impact Score (1-10):
   - 10 = Market-changing major news (Fed decisions, huge M&A)
   - 8-9 = High impact (major earnings, significant AI news)
   - 6-7 = Medium impact (product launches, analyst upgrades)
   - 5 = Moderate impact (routine updates, minor developments)
   - 1-4 = Low impact (minor news, routine coverage)
3. Price Impact: "positive", "negative", or "neutral"
4. Categories:
   - earnings: Quarterly results, revenue/profit reports
   - m&a: Mergers, acquisitions, IPOs
   - tech-ai: Technology developments, AI partnerships
   - macro: Economic data, Fed policy, market-wide effects
   - trading: Trading updates, stock movements, volume
5. Market Significance: How this affects broader market

Priority Factors:
- Large-cap stocks have higher impact
- Earnings announcements are high priority
- M&A activities are very high impact
- Tech/AI developments in 2024 are high impact
- Fed/macro news affecting S&P500 is significant

Return ONLY the JSON response, no additional text.
"""

        return prompt

    def _parse_analysis_response(self, response: str, article: Dict) -> Optional[Dict]:
        """Parse GLM response and combine with article data"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.error(f"No JSON found in response: {response[:100]}...")
                return None

            json_str = response[json_start:json_end]
            analysis_data = json.loads(json_str)

            # Combine with original article data
            combined_data = {
                'original_article': article,
                'analysis': analysis_data,
                'combined_score': self._calculate_combined_score(analysis_data, article)
            }

            return combined_data

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response: {response}")
            return None
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return None

    def _calculate_combined_score(self, analysis: Dict, article: Dict) -> int:
        """Calculate combined impact score"""
        base_score = analysis.get('impact_score', 5)

        # Boost score for large-cap stocks
        tickers = analysis.get('tickers', [])
        large_cap_count = sum(1 for ticker in tickers if ticker in LARGE_CAP_STOCKS)
        if large_cap_count > 0:
            base_score += min(large_cap_count, 2)  # Max +2 for multiple large-caps

        # Boost for reliable sources
        source = article.get('source', '').lower()
        reliable_sources = ['bloomberg', 'reuters', 'wsj', 'cnbc', 'yahoo finance']
        if any(rel in source for rel in reliable_sources):
            base_score += 1

        # Cap at 10
        return min(base_score, 10)

    def get_analysis_summary(self, analyzed_articles: List[Dict]) -> Dict:
        """Get summary of analysis results"""
        if not analyzed_articles:
            return {
                'total_analyzed': 0,
                'high_impact': 0,
                'medium_impact': 0,
                'categories': {},
                'top_tickers': []
            }

        total = len(analyzed_articles)
        high_impact = sum(1 for a in analyzed_articles if a['analysis']['impact_score'] >= 8)
        medium_impact = sum(1 for a in analyzed_articles if 5 <= a['analysis']['impact_score'] <= 7)

        # Count categories
        categories = {}
        for article in analyzed_articles:
            category = article['analysis'].get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1

        # Count tickers
        ticker_counts = {}
        for article in analyzed_articles:
            tickers = article['analysis'].get('tickers', [])
            for ticker in tickers:
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

        top_tickers = sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            'total_analyzed': total,
            'high_impact': high_impact,
            'medium_impact': medium_impact,
            'categories': categories,
            'top_tickers': top_tickers
        }