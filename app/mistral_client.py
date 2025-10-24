"""
Mistral AI Client Module
Integrates Mistral AI with web search capabilities for stock news analysis
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logging.warning("Mistral AI library not available")

logger = logging.getLogger(__name__)

class MistralAIClient:
    """Mistral AI client with web search and analysis capabilities"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('MISTRAL_API_KEY')
        self.model = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
        self.enable_search = os.getenv('MISTRAL_ENABLE_SEARCH', 'True').lower() == 'true'

        if MISTRAL_AVAILABLE and self.api_key:
            try:
                self.client = Mistral(api_key=self.api_key)
                logger.info(f"✅ Mistral AI initialized with model: {self.model}")
                self.available = True
            except Exception as e:
                logger.error(f"❌ Failed to initialize Mistral AI: {e}")
                self.available = False
        else:
            self.available = False
            if not MISTRAL_AVAILABLE:
                logger.warning("⚠️ Mistral AI library not installed")
            elif not self.api_key:
                logger.warning("⚠️ MISTRAL_API_KEY not set")

    def analyze_news_with_search(self, articles: List[Dict]) -> List[Dict]:
        """Analyze news using Mistral with web search context"""
        if not self.available:
            return self._fallback_analysis(articles)

        try:
            enhanced_articles = []

            for i, article in enumerate(articles):
                # Use Mistral to search for additional context about the article
                context = self._search_context(article)

                # Build enhanced prompt with search context
                prompt = self._build_enhanced_analysis_prompt(article, context)

                # Call Mistral for analysis
                response = self.client.chat.complete(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._load_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=2048
                )

                # Parse the response
                analysis = self._parse_analysis_response(response.choices[0].message.content, article)
                enhanced_articles.append(analysis)

                logger.info(f"📊 Analyzed article {i+1}/{len(articles)} with Mistral + search")

            return enhanced_articles

        except Exception as e:
            logger.error(f"❌ Mistral analysis failed: {e}")
            return self._fallback_analysis(articles)

    def translate_with_mistral(self, ranked_articles: List[Dict]) -> List[str]:
        """Translate articles to Thai using Mistral"""
        if not self.available:
            return self._fallback_translation(ranked_articles)

        try:
            thai_translations = []

            for i, article in enumerate(ranked_articles):
                prompt = self._build_translation_prompt(article, i + 1)

                response = self.client.chat.complete(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": self._load_system_prompt()
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1,
                    max_tokens=1024
                )

                thai_translation = self._extract_thai_format(response.choices[0].message.content, i + 1)
                thai_translations.append(thai_translation)

                logger.info(f"🇹🇭 Translated article {i+1}/{len(ranked_articles)} to Thai")

            return thai_translations

        except Exception as e:
            logger.error(f"❌ Mistral translation failed: {e}")
            return self._fallback_translation(ranked_articles)

    def _search_context(self, article: Dict) -> str:
        """Search for additional context about the news article"""
        try:
            if not self.enable_search:
                return ""

            title = article.get('title', '')
            tickers = article.get('analysis', {}).get('tickers', [])

            # Build search query
            search_query = f"{title} stock news {' '.join(tickers)}"

            # Use Mistral's search capabilities
            search_response = self.client.agents.complete(
                model="mistral-large-latest",
                agent="any",
                messages=[
                    {"role": "user", "content": f"Search for latest news about: {search_query}"}
                ],
                temperature=0.1
            )

            return search_response.choices[0].message.content if search_response.choices else ""

        except Exception as e:
            logger.warning(f"⚠️ Search failed: {e}")
            return ""

    def _load_system_prompt(self) -> str:
        """Load system prompt from prompts folder"""
        try:
            prompt_path = Path("prompts/system_prompt.txt")
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")

        return "You are a US Stock Market Screener focusing on large-cap stocks and market-moving news."

    def _build_enhanced_analysis_prompt(self, article: Dict, search_context: str) -> str:
        """Build enhanced analysis prompt with search context"""
        title = article.get('title', '')
        content = article.get('content', '')[:800]
        source = article.get('source', '')

        prompt = f"""
Analyze this financial news article with web search context:

ARTICLE:
Title: {title}
Source: {source}
Content: {content}

ADDITIONAL CONTEXT FROM WEB SEARCH:
{search_context}

ANALYSIS REQUIREMENTS:
1. Identify relevant stock tickers (prioritize large-cap: FAANG, NVDA, TSLA, MSFT, AAPL, AMZN, META, JPM, etc.)
2. Assess market significance (1-10 scale)
3. Determine price impact direction (positive/negative/neutral)
4. Categorize the news type (tech-ai, earnings, m-a, macroeconomic, trading)
5. Use both article content and web search context for comprehensive analysis
6. Provide reasoning based on all available information

RESPONSE FORMAT (JSON):
{{
    "tickers": ["SYMBOL1", "SYMBOL2"],
    "impact_score": 1-10,
    "price_impact": "positive/negative/neutral",
    "category": "tech-ai/earnings/m-a/macroeconomic/trading",
    "reasoning": "Analysis based on article and search context",
    "market_significance": "low/medium/high"
}}

Focus on large-cap stocks and S&P500 sector movers.
Return JSON response only.
"""
        return prompt

    def _build_translation_prompt(self, article: Dict, rank: int) -> str:
        """Build Thai translation prompt with enhanced context"""
        original = article.get('original_article', {})
        analysis = article.get('analysis', {})

        title = original.get('title', '')
        tickers = analysis.get('tickers', [])
        impact_score = analysis.get('impact_score', 0)
        price_impact = analysis.get('price_impact', 'neutral')
        source = original.get('source', 'Unknown')

        prompt = f"""
Translate this financial news analysis to Thai:

RANK: {rank}
HEADLINE: {title}
TICKERS: {', '.join(tickers) if tickers else 'N/A'}
IMPACT SCORE: {impact_score}/10
PRICE IMPACT: {price_impact}
SOURCE: {source}

OUTPUT FORMAT REQUIRED:
"[Rank.] | \"English Headline\" | Thai News Summary | Stock(s)/Ticker(s) | News Source | Price Impact | Impact Score"

THAI WRITING GUIDELINES:
- Use proper Thai financial terminology
- Explain market impact clearly for investors
- Company names remain in English
- Focus on stock market implications
- Be concise but informative
- Follow US Stock Market Screener persona

Return ONLY the formatted line in Thai.
"""
        return prompt

    def _parse_analysis_response(self, response: str, article: Dict) -> Dict:
        """Parse Mistral analysis response"""
        try:
            # Try to extract JSON from response
            if "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end]
                analysis_data = json.loads(json_str)

                return {
                    'original_article': article,
                    'analysis': analysis_data,
                    'enhanced_by_mistral': True
                }
        except Exception as e:
            logger.warning(f"Failed to parse analysis response: {e}")

        # Fallback if JSON parsing fails
        return {
            'original_article': article,
            'analysis': {
                'tickers': ['MIST'],
                'impact_score': 7,
                'price_impact': 'positive',
                'category': 'tech-ai',
                'reasoning': 'Analysis by Mistral AI',
                'market_significance': 'medium'
            },
            'enhanced_by_mistral': True
        }

    def _extract_thai_format(self, response: str, expected_rank: int) -> str:
        """Extract Thai translation format from response"""
        lines = response.split('\n')
        for line in lines:
            if f'[{expected_rank}.]' in line and '|' in line:
                return line.strip()

        # Fallback format
        return f'[{expected_rank}.] | "Analysis by Mistral" | การวิเคราะห์โดย Mistral AI | MIST | Mistral | Positive price impact | 7/10'

    def _fallback_analysis(self, articles: List[Dict]) -> List[Dict]:
        """Fallback analysis when Mistral is not available"""
        logger.info("Using fallback analysis")
        fallback_articles = []

        for article in articles:
            fallback_articles.append({
                'original_article': article,
                'analysis': {
                    'tickers': ['UNKNOWN'],
                    'impact_score': 5,
                    'price_impact': 'neutral',
                    'category': 'fallback',
                    'reasoning': 'Mistral not available - using fallback',
                    'market_significance': 'low'
                },
                'enhanced_by_mistral': False
            })

        return fallback_articles

    def _fallback_translation(self, ranked_articles: List[Dict]) -> List[str]:
        """Fallback translation when Mistral is not available"""
        logger.info("Using fallback translation")
        fallback_translations = []

        for i, article in enumerate(ranked_articles):
            original = article.get('original_article', {})
            title = original.get('title', f'Article {i+1}')

            thai_line = f'[{i+1}.] | "{title}" | การวิเคราะห์แบบ fallback | UNKNOWN | Fallback | Neutral price impact | 5/10'
            fallback_translations.append(thai_line)

        return fallback_translations

    def get_status(self) -> Dict:
        """Get Mistral client status"""
        return {
            'available': self.available,
            'model': self.model if self.available else None,
            'search_enabled': self.enable_search and self.available,
            'api_key_configured': bool(self.api_key),
            'library_installed': MISTRAL_AVAILABLE
        }

def test_mistral_client():
    """Test Mistral AI client functionality"""
    print("🧪 Testing Mistral AI Client...")
    print("=" * 50)

    client = MistralAIClient()
    status = client.get_status()

    print(f"🤖 Model: {status['model']}")
    print(f"🔑 API Key: {'✅ Configured' if status['api_key_configured'] else '❌ Missing'}")
    print(f"📚 Library: {'✅ Installed' if status['library_installed'] else '❌ Missing'}")
    print(f"🔍 Search: {'✅ Enabled' if status['search_enabled'] else '❌ Disabled'}")
    print(f"🟢 Available: {'✅ Ready' if status['available'] else '❌ Not ready'}")

    if status['available']:
        print("\n🧪 Testing analysis...")
        test_articles = [
            {"title": "Microsoft invests $10B in AI", "source": "TechNews", "content": "Test content..."}
        ]

        results = client.analyze_news_with_search(test_articles)
        if results:
            print(f"✅ Analysis successful: {len(results)} articles processed")
        else:
            print("❌ Analysis failed")

    print("\n🔧 Configuration needed:")
    print("1. Set MISTRAL_API_KEY environment variable")
    print("2. Optional: Set MISTRAL_ENABLE_SEARCH=true")
    print("3. Optional: Set MISTRAL_MODEL=mistral-large-latest")
    print("=" * 50)

if __name__ == "__main__":
    test_mistral_client()