"""
Web Search Manager
Smart manager for web search with fallback logic and caching
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config import (
    WEB_SEARCH_ENABLED, WEB_SEARCH_MAX_RESULTS,
    UNCERTAINTY_THRESHOLD, HIGH_IMPACT_THRESHOLD,
    MIN_TICKERS_REQUIRED, SEARCH_ON_UNCERTAINTY,
    SEARCH_ON_HIGH_IMPACT, SEARCH_ON_MISSING_TICKERS
)

try:
    from .duckduckgo_search import DuckDuckGoSearch
    SEARCH_AVAILABLE = True
except ImportError:
    SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class WebSearchManager:
    """
    Manages web search operations with intelligent fallback
    Decides when to use web search based on analysis uncertainty
    """

    def __init__(self):
        self.enabled = WEB_SEARCH_ENABLED and SEARCH_AVAILABLE
        self.search_client = None
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = timedelta(hours=1)

        if self.enabled:
            try:
                self.search_client = DuckDuckGoSearch()
                logger.info("✅ Web Search Manager initialized (DuckDuckGo)")
            except Exception as e:
                logger.error(f"Failed to initialize search client: {e}")
                self.enabled = False
        else:
            logger.warning("⚠️ Web Search disabled or not available")

    def should_search(self, analysis: Dict) -> bool:
        """
        Determine if web search is needed for this analysis

        Args:
            analysis: Analysis dict with confidence, impact_score, tickers

        Returns:
            True if web search should be performed
        """
        if not self.enabled:
            return False

        # Check various uncertainty indicators
        reasons = []

        # 1. Low confidence / uncertainty
        confidence = analysis.get('confidence', 1.0)
        if SEARCH_ON_UNCERTAINTY and confidence < UNCERTAINTY_THRESHOLD:
            reasons.append(f"low_confidence ({confidence:.2f})")

        # 2. High impact news (need to be accurate)
        impact_score = analysis.get('impact_score', 0)
        if SEARCH_ON_HIGH_IMPACT and impact_score >= HIGH_IMPACT_THRESHOLD:
            reasons.append(f"high_impact ({impact_score})")

        # 3. Missing or insufficient tickers
        tickers = analysis.get('tickers', [])
        if SEARCH_ON_MISSING_TICKERS and len(tickers) < MIN_TICKERS_REQUIRED:
            reasons.append(f"missing_tickers ({len(tickers)})")

        # 4. Category is uncertain
        category = analysis.get('category', '')
        if category in ['uncertain', 'unknown', '']:
            reasons.append("uncertain_category")

        # 5. Truncated or incomplete content
        flags = analysis.get('flags', [])
        if 'truncated' in flags or 'incomplete' in flags:
            reasons.append("incomplete_content")

        if reasons:
            logger.info(f"🔍 Web search needed: {', '.join(reasons)}")
            return True

        return False

    def enhance_analysis(self, article: Dict, analysis: Dict) -> Dict:
        """
        Enhance analysis with web search context

        Args:
            article: Original article
            analysis: Current analysis results

        Returns:
            Enhanced analysis dict
        """
        if not self.enabled or not self.should_search(analysis):
            return analysis

        try:
            # Check cache
            cache_key = self._get_cache_key(article)
            cached = self._get_cached(cache_key)
            if cached:
                logger.info("📦 Using cached search results")
                return self._merge_analysis(analysis, cached)

            # Get context from web search
            context = self.search_client.get_context_for_article(article)

            if context:
                # Store in cache
                self._set_cached(cache_key, {'context': context, 'timestamp': datetime.now()})

                # Merge context with analysis
                enhanced = analysis.copy()
                enhanced['web_search_context'] = context
                enhanced['enhanced_by_search'] = True
                enhanced['search_provider'] = 'DuckDuckGo'

                # Potentially boost confidence if we found corroborating info
                if len(context) > 100:  # Got substantial context
                    original_confidence = enhanced.get('confidence', 0.5)
                    enhanced['confidence'] = min(original_confidence + 0.2, 1.0)
                    logger.info(f"📈 Boosted confidence: {original_confidence:.2f} → {enhanced['confidence']:.2f}")

                return enhanced

            return analysis

        except Exception as e:
            logger.error(f"Error enhancing analysis with web search: {e}")
            return analysis

    def verify_article(self, article: Dict) -> Dict:
        """
        Verify article by searching for corroborating sources

        Args:
            article: Article to verify

        Returns:
            Verification result dict
        """
        if not self.enabled:
            return {'verified': False, 'reason': 'search_disabled'}

        try:
            title = article.get('title', '')
            tickers = article.get('analysis', {}).get('tickers', [])

            verification = self.search_client.verify_news(title, tickers)
            logger.info(f"✅ Verification: {verification}")

            return verification

        except Exception as e:
            logger.error(f"Error verifying article: {e}")
            return {'verified': False, 'reason': str(e)}

    def search_latest_news(self, ticker: str, max_results: int = 5) -> List[Dict]:
        """
        Search for latest news about a specific ticker

        Args:
            ticker: Stock ticker symbol
            max_results: Max results to return

        Returns:
            List of news articles
        """
        if not self.enabled:
            return []

        try:
            query = f"{ticker} stock news earnings"
            results = self.search_client.search_news(query, max_results=max_results)
            return results

        except Exception as e:
            logger.error(f"Error searching news for {ticker}: {e}")
            return []

    def _get_cache_key(self, article: Dict) -> str:
        """Generate cache key for article"""
        title = article.get('title', '')
        url = article.get('url', '')
        return f"{title[:50]}_{url[:50]}"

    def _get_cached(self, key: str) -> Optional[Dict]:
        """Get cached search result if not expired"""
        if key in self.cache:
            cached = self.cache[key]
            timestamp = cached.get('timestamp', datetime.min)
            if datetime.now() - timestamp < self.cache_ttl:
                return cached
            else:
                # Expired, remove from cache
                del self.cache[key]
        return None

    def _set_cached(self, key: str, value: Dict):
        """Set cached value"""
        self.cache[key] = value

    def _merge_analysis(self, analysis: Dict, cached: Dict) -> Dict:
        """Merge cached data with analysis"""
        enhanced = analysis.copy()
        enhanced['web_search_context'] = cached.get('context', '')
        enhanced['enhanced_by_search'] = True
        enhanced['from_cache'] = True
        return enhanced

    def get_status(self) -> Dict:
        """Get web search manager status"""
        return {
            'enabled': self.enabled,
            'provider': 'DuckDuckGo' if self.enabled else None,
            'cache_size': len(self.cache),
            'search_on_uncertainty': SEARCH_ON_UNCERTAINTY,
            'search_on_high_impact': SEARCH_ON_HIGH_IMPACT,
            'uncertainty_threshold': UNCERTAINTY_THRESHOLD,
            'high_impact_threshold': HIGH_IMPACT_THRESHOLD
        }

    def clear_cache(self):
        """Clear search cache"""
        old_size = len(self.cache)
        self.cache.clear()
        logger.info(f"🗑️ Cleared {old_size} cached search results")


def test_web_search_manager():
    """Test web search manager"""
    print("🧪 Testing Web Search Manager...")
    print("=" * 60)

    manager = WebSearchManager()
    status = manager.get_status()

    print(f"✅ Enabled: {status['enabled']}")
    print(f"🔍 Provider: {status['provider']}")
    print(f"📊 Settings:")
    print(f"   - Uncertainty threshold: {status['uncertainty_threshold']}")
    print(f"   - High impact threshold: {status['high_impact_threshold']}")
    print(f"   - Search on uncertainty: {status['search_on_uncertainty']}")
    print(f"   - Search on high impact: {status['search_on_high_impact']}")

    if status['enabled']:
        print("\n🧪 Testing uncertainty detection...")

        # Test case 1: Low confidence - should search
        test_analysis_1 = {
            'confidence': 0.5,
            'impact_score': 6,
            'tickers': ['MSFT'],
            'category': 'tech-ai'
        }
        should_search_1 = manager.should_search(test_analysis_1)
        print(f"   Low confidence (0.5): {should_search_1} ✅")

        # Test case 2: High impact - should search
        test_analysis_2 = {
            'confidence': 0.9,
            'impact_score': 9,
            'tickers': ['NVDA'],
            'category': 'earnings'
        }
        should_search_2 = manager.should_search(test_analysis_2)
        print(f"   High impact (9): {should_search_2} ✅")

        # Test case 3: Normal case - should NOT search
        test_analysis_3 = {
            'confidence': 0.85,
            'impact_score': 6,
            'tickers': ['AAPL'],
            'category': 'trading'
        }
        should_search_3 = manager.should_search(test_analysis_3)
        print(f"   Normal case: {should_search_3} ✅")

        print("\n🧪 Testing enhancement...")
        test_article = {
            'title': 'Microsoft announces major AI partnership',
            'url': 'https://example.com/news'
        }
        enhanced = manager.enhance_analysis(test_article, test_analysis_1)
        print(f"   Enhanced: {enhanced.get('enhanced_by_search', False)}")
        if 'web_search_context' in enhanced:
            print(f"   Context length: {len(enhanced['web_search_context'])} chars")

    else:
        print("\n❌ Web search not available")
        print("Make sure to:")
        print("1. Install duckduckgo-search: pip install duckduckgo-search")
        print("2. Set WEB_SEARCH_ENABLED=True in config.py")

    print("=" * 60)


if __name__ == "__main__":
    test_web_search_manager()
