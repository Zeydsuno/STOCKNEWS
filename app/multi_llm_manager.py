"""
Multi-LLM Manager
Handles multiple LLM providers with Mistral AI as primary
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union
from pathlib import Path

# Import LLM providers
try:
    from app.mistral_client import MistralAIClient
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

try:
    from app.langchain_integration import LangChainStockAnalyzer
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from config import (
    MISTRAL_API_KEY, MISTRAL_MODEL, MISTRAL_ENABLE_SEARCH,
    GLM_API_KEY, WEB_SEARCH_ENABLED
)

# Import web search manager
try:
    from app.search.web_search_manager import WebSearchManager
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class MultiLLMManager:
    """Manages multiple LLM providers with intelligent fallback"""

    def __init__(self):
        self.providers = {}
        self.primary_provider = None
        self.fallback_providers = []
        self.web_search = None

        self._initialize_providers()
        self._initialize_web_search()

    def _initialize_providers(self):
        """Initialize available LLM providers in priority order"""

        # 1. Mistral AI (Primary choice - free and has web search)
        if MISTRAL_AVAILABLE and MISTRAL_API_KEY:
            try:
                self.primary_provider = MistralAIClient(api_key=MISTRAL_API_KEY)
                self.providers['mistral'] = self.primary_provider
                logger.info("✅ Mistral AI initialized as primary provider")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Mistral AI: {e}")

        # 2. LangChain (Fallback - uses your prompts)
        if LANGCHAIN_AVAILABLE and GLM_API_KEY:
            try:
                langchain_provider = LangChainStockAnalyzer()
                self.providers['langchain'] = langchain_provider
                self.fallback_providers.append(langchain_provider)
                logger.info("✅ LangChain initialized as fallback provider")
            except Exception as e:
                logger.error(f"❌ Failed to initialize LangChain: {e}")

        # 3. Mock Fallback (Always available)
        self.providers['mock'] = MockLLMProvider()
        self.fallback_providers.append(self.providers['mock'])

        logger.info(f"🔧 Initialized {len(self.providers)} LLM providers")
        logger.info(f"🎯 Primary: {type(self.primary_provider).__name__ if self.primary_provider else 'None'}")

    def _initialize_web_search(self):
        """Initialize web search manager for fallback"""
        if WEB_SEARCH_ENABLED and WEB_SEARCH_AVAILABLE:
            try:
                self.web_search = WebSearchManager()
                logger.info("✅ Web Search Manager initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Web Search: {e}")
        else:
            logger.info("ℹ️ Web Search disabled or not available")

    def analyze_news(self, articles: List[Dict]) -> List[Dict]:
        """Analyze news using available LLM providers with fallback + web search"""
        if not articles:
            return []

        analyzed_articles = []

        # Try primary provider first
        if self.primary_provider and hasattr(self.primary_provider, 'analyze_news_with_search'):
            try:
                logger.info("🚀 Using Mistral AI with web search for analysis")
                results = self.primary_provider.analyze_news_with_search(articles)
                if results:
                    analyzed_articles = results
                else:
                    logger.warning("⚠️ Mistral AI analysis failed, trying fallback")
            except Exception as e:
                logger.error(f"❌ Primary provider failed: {e}")

        # Try fallback providers if primary failed
        if not analyzed_articles:
            for provider in self.fallback_providers:
                try:
                    provider_name = type(provider).__name__
                    logger.info(f"🔄 Trying fallback provider: {provider_name}")

                    if provider_name == "LangChainStockAnalyzer":
                        # Use existing LangChain logic
                        enhanced_articles = []
                        for article in articles:
                            analysis = provider.analyze_article(article)
                            if analysis:
                                enhanced_articles.append(analysis)
                        analyzed_articles = enhanced_articles
                        break

                    elif provider_name == "MockLLMProvider":
                        analyzed_articles = provider.analyze_articles(articles)
                        break

                except Exception as e:
                    logger.error(f"❌ Fallback provider {provider_name} failed: {e}")
                    continue

        # Enhancement with web search (if enabled)
        if self.web_search and analyzed_articles:
            logger.info("🔍 Checking if web search enhancement is needed...")
            enhanced_count = 0

            for i, analyzed_article in enumerate(analyzed_articles):
                try:
                    analysis = analyzed_article.get('analysis', {})

                    # Check if we should search
                    if self.web_search.should_search(analysis):
                        original_article = analyzed_article.get('original_article', {})
                        enhanced_analysis = self.web_search.enhance_analysis(original_article, analysis)

                        if enhanced_analysis.get('enhanced_by_search'):
                            analyzed_articles[i]['analysis'] = enhanced_analysis
                            enhanced_count += 1
                            logger.info(f"✅ Enhanced article {i+1}/{len(analyzed_articles)} with web search")

                except Exception as e:
                    logger.error(f"Error enhancing article {i+1}: {e}")
                    continue

            if enhanced_count > 0:
                logger.info(f"🎯 Enhanced {enhanced_count}/{len(analyzed_articles)} articles with web search")

        if not analyzed_articles:
            logger.error("❌ All LLM providers failed")

        return analyzed_articles

    def translate_to_thai(self, ranked_articles: List[Dict]) -> List[str]:
        """Translate to Thai using available LLM providers"""
        if not ranked_articles:
            return []

        # Try primary provider first
        if self.primary_provider and hasattr(self.primary_provider, 'translate_with_mistral'):
            try:
                logger.info("🚀 Using Mistral AI for translation")
                results = self.primary_provider.translate_with_mistral(ranked_articles)
                if results:
                    return results
                logger.warning("⚠️ Mistral AI translation failed, trying fallback")
            except Exception as e:
                logger.error(f"❌ Primary provider failed: {e}")

        # Try fallback providers
        for provider in self.fallback_providers:
            try:
                provider_name = type(provider).__name__
                logger.info(f"🔄 Trying fallback translator: {provider_name}")

                if provider_name == "LangChainStockAnalyzer":
                    return provider.translate_ranked_news(ranked_articles)

                elif provider_name == "MockLLMProvider":
                    return provider.translate_articles(ranked_articles)

            except Exception as e:
                logger.error(f"❌ Fallback translator {provider_name} failed: {e}")
                continue

        logger.error("❌ All translation providers failed")
        return []

    def get_status(self) -> Dict:
        """Get status of all LLM providers and web search"""
        status = {
            'total_providers': len(self.providers),
            'active_primary': type(self.primary_provider).__name__ if self.primary_provider else None,
            'fallback_count': len(self.fallback_providers),
            'web_search_enabled': self.web_search is not None,
            'providers': {},
            'web_search': {}
        }

        for name, provider in self.providers.items():
            if hasattr(provider, 'get_status'):
                status['providers'][name] = provider.get_status()

        if self.web_search:
            status['web_search'] = self.web_search.get_status()

        return status

class MockLLMProvider:
    """Mock LLM provider for testing and fallback"""

    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """Mock analysis of articles"""
        analyzed_articles = []

        for i, article in enumerate(articles):
            analyzed_article = {
                'original_article': article,
                'analysis': {
                    'tickers': ['MOCK'],
                    'impact_score': min(8, len(articles) - i),  # Decreasing scores
                    'price_impact': 'positive' if i % 2 == 0 else 'negative',
                    'category': 'mock-analysis',
                    'reasoning': f'Mock analysis for article {i+1}',
                    'market_significance': 'medium'
                },
                'enhanced_by_mistral': False
            }
            analyzed_articles.append(analyzed_article)

        logger.info(f"🧪 Mock analyzed {len(analyzed_articles)} articles")
        return analyzed_articles

    def translate_articles(self, ranked_articles: List[Dict]) -> List[str]:
        """Mock Thai translation"""
        translations = []

        for i, article in enumerate(ranked_articles):
            original = article.get('original_article', {})
            title = original.get('title', f'Mock Article {i+1}')

            thai_line = f'[{i+1}.] | "{title}" | การวิเคราะห์แบบ mock | MOCK | Mock Source | Mock price impact | 5/10'
            translations.append(thai_line)

        logger.info(f"🧪 Mock translated {len(translations)} articles")
        return translations

    def get_status(self) -> Dict:
        """Get mock provider status"""
        return {
            'available': True,
            'library': 'Mock',
            'description': 'Always available mock provider'
        }

def test_multi_llm_manager():
    """Test multi-LLM manager functionality"""
    print("🧪 Testing Multi-LLM Manager...")
    print("=" * 60)

    manager = MultiLLMManager()
    status = manager.get_status()

    print(f"🤖 Providers: {status['total_providers']}")
    print(f"🎯 Primary: {status['active_primary']}")
    print(f"🔄 Fallbacks: {status['fallback_count']}")

    print("\n📊 Provider Status:")
    for name, provider_status in status['providers'].items():
        print(f"  • {name}: {provider_status}")

    # Test analysis
    test_articles = [
        {"title": "Microsoft AI investment", "source": "TechNews", "content": "Test..."},
        {"title": "Tesla earnings", "source": "FinanceNews", "content": "Test..."}
    ]

    print(f"\n🧪 Testing analysis with {len(test_articles)} articles...")
    analysis_results = manager.analyze_news(test_articles)
    print(f"✅ Analysis completed: {len(analysis_results)} results")

    # Test translation
    print(f"\n🧪 Testing translation with {len(analysis_results)} articles...")
    translation_results = manager.translate_to_thai(analysis_results)
    print(f"✅ Translation completed: {len(translation_results)} results")

    print(f"\n🔧 Setup Instructions:")
    print(f"1. Set MISTRAL_API_KEY environment variable for primary provider")
    print(f"2. Set MISTRAL_ENABLE_SEARCH=true for web search")
    print(f"3. Fallback providers available automatically")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_llm_manager()