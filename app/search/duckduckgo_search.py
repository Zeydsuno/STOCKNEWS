"""
DuckDuckGo Web Search Integration
Free, no API key required
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False
    logging.warning("duckduckgo-search not installed. Install with: pip install duckduckgo-search")

logger = logging.getLogger(__name__)

class DuckDuckGoSearch:
    """DuckDuckGo web search client"""

    def __init__(self):
        self.available = DDGS_AVAILABLE
        if not self.available:
            logger.warning("⚠️ DuckDuckGo search not available - library not installed")

    def search(self, query: str, max_results: int = 5, region: str = 'us-en') -> List[Dict]:
        """
        Search the web using DuckDuckGo

        Args:
            query: Search query
            max_results: Maximum number of results to return
            region: Region code (default: us-en for US English)

        Returns:
            List of search results with title, href, body
        """
        if not self.available:
            logger.error("DuckDuckGo search not available")
            return []

        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    region=region,
                    safesearch='off',
                    max_results=max_results
                ))

                logger.info(f"🔍 DuckDuckGo search: '{query}' → {len(results)} results")
                return results

        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

    def search_news(self, query: str, max_results: int = 5, region: str = 'us-en') -> List[Dict]:
        """
        Search news using DuckDuckGo News

        Args:
            query: Search query
            max_results: Maximum number of results
            region: Region code

        Returns:
            List of news results
        """
        if not self.available:
            logger.error("DuckDuckGo search not available")
            return []

        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(
                    query,
                    region=region,
                    safesearch='off',
                    max_results=max_results
                ))

                logger.info(f"📰 DuckDuckGo news: '{query}' → {len(results)} results")
                return results

        except Exception as e:
            logger.error(f"DuckDuckGo news search error: {e}")
            return []

    def get_context_for_article(self, article: Dict, max_results: int = 3) -> str:
        """
        Get additional context for a news article

        Args:
            article: Article dict with 'title' and optional 'tickers'
            max_results: Number of search results to fetch

        Returns:
            Formatted context string
        """
        if not self.available:
            return ""

        try:
            title = article.get('title', '')
            tickers = article.get('analysis', {}).get('tickers', [])

            # Build search query
            query_parts = [title]
            if tickers:
                query_parts.append(' '.join(tickers[:3]))  # Top 3 tickers
            query_parts.append('stock news')

            search_query = ' '.join(query_parts)

            # Search for context
            results = self.search_news(search_query, max_results=max_results)

            if not results:
                return ""

            # Format context
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"{i}. {result.get('title', '')}")
                body = result.get('body', '')
                if body:
                    context_parts.append(f"   {body[:200]}...")

            context = "\n".join(context_parts)
            logger.info(f"✅ Retrieved context for: {title[:50]}...")

            return context

        except Exception as e:
            logger.error(f"Error getting context: {e}")
            return ""

    def verify_news(self, headline: str, tickers: List[str] = None) -> Dict:
        """
        Verify news by searching for corroborating sources

        Args:
            headline: News headline to verify
            tickers: Related stock tickers

        Returns:
            Dict with verification results
        """
        if not self.available:
            return {'verified': False, 'sources': 0, 'confidence': 0}

        try:
            # Build verification query
            query = headline
            if tickers:
                query += f" {' '.join(tickers[:2])}"

            results = self.search_news(query, max_results=10)

            # Count unique sources
            sources = set()
            for result in results:
                source = result.get('source', '')
                if source:
                    sources.add(source.lower())

            verified = len(sources) >= 2  # At least 2 sources
            confidence = min(len(sources) / 5.0, 1.0)  # 0-1 scale, max at 5 sources

            return {
                'verified': verified,
                'sources': len(sources),
                'confidence': confidence,
                'results_found': len(results)
            }

        except Exception as e:
            logger.error(f"Error verifying news: {e}")
            return {'verified': False, 'sources': 0, 'confidence': 0}

    def get_status(self) -> Dict:
        """Get DuckDuckGo search status"""
        return {
            'available': self.available,
            'provider': 'DuckDuckGo',
            'cost': 'Free',
            'api_key_required': False,
            'rate_limits': 'Yes (but generous)',
            'library': 'duckduckgo-search'
        }


def test_duckduckgo_search():
    """Test DuckDuckGo search functionality"""
    print("🧪 Testing DuckDuckGo Search...")
    print("=" * 60)

    ddg = DuckDuckGoSearch()
    status = ddg.get_status()

    print(f"🔍 Provider: {status['provider']}")
    print(f"💰 Cost: {status['cost']}")
    print(f"🔑 API Key: {status['api_key_required']}")
    print(f"✅ Available: {status['available']}")

    if status['available']:
        print("\n🧪 Testing web search...")
        results = ddg.search("Microsoft AI investment stock news", max_results=3)
        print(f"✅ Found {len(results)} results")

        if results:
            print("\nFirst result:")
            print(f"  Title: {results[0].get('title', '')[:60]}...")
            print(f"  URL: {results[0].get('href', '')}")

        print("\n🧪 Testing news search...")
        news_results = ddg.search_news("Tesla stock earnings", max_results=3)
        print(f"✅ Found {len(news_results)} news results")

        print("\n🧪 Testing article context...")
        test_article = {
            'title': 'NVIDIA announces partnership',
            'analysis': {'tickers': ['NVDA']}
        }
        context = ddg.get_context_for_article(test_article, max_results=2)
        print(f"✅ Context length: {len(context)} characters")

    else:
        print("\n❌ DuckDuckGo search not available")
        print("Install with: pip install duckduckgo-search")

    print("=" * 60)


if __name__ == "__main__":
    test_duckduckgo_search()
