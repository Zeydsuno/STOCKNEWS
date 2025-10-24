import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# Import all components
from app.collectors.base_collector import NewsCollectorManager
from app.collectors.newsapi_collector import NewsAPICollector
from app.collectors.rss_collector import RSSCollector
from app.collectors.alphavantage_collector import AlphaVantageCollector
from app.analysis.news_analyzer import NewsImpactAnalyzer
from app.analysis.news_ranker import NewsRanker
from app.translation.thai_translator import ThaiNewsTranslator

logger = logging.getLogger(__name__)

class StockNewsPipeline:
    """Complete pipeline for stock news processing"""

    def __init__(self):
        # Initialize collectors
        self.collector_manager = NewsCollectorManager()
        self._setup_collectors()

        # Initialize analyzers
        self.news_analyzer = NewsImpactAnalyzer()
        self.news_ranker = NewsRanker()

        # Initialize translator
        self.thai_translator = ThaiNewsTranslator()

        # Pipeline stats
        self.last_run = None
        self.last_results = None

    def _setup_collectors(self):
        """Setup all news collectors"""
        try:
            # Add NewsAPI collector
            newsapi_collector = NewsAPICollector()
            self.collector_manager.add_collector(newsapi_collector)
            logger.info("✅ NewsAPI collector initialized")

        except Exception as e:
            logger.warning(f"⚠️ NewsAPI collector failed: {e}")

        try:
            # Add RSS collector
            rss_collector = RSSCollector()
            self.collector_manager.add_collector(rss_collector)
            logger.info("✅ RSS collector initialized")

        except Exception as e:
            logger.warning(f"⚠️ RSS collector failed: {e}")

        try:
            # Add Alpha Vantage collector
            av_collector = AlphaVantageCollector()
            self.collector_manager.add_collector(av_collector)
            logger.info("✅ Alpha Vantage collector initialized")

        except Exception as e:
            logger.warning(f"⚠️ Alpha Vantage collector failed: {e}")

    def run_complete_pipeline(self, hours: int = 3) -> Dict:
        """Run the complete pipeline and return results"""
        start_time = time.time()
        logger.info(f"🚀 Starting Stock News Pipeline for last {hours} hours")

        try:
            # Step 1: Collect news
            logger.info("📰 Step 1: Collecting news from all sources...")
            raw_articles = self._collect_news()

            if not raw_articles:
                logger.warning("❌ No news articles collected")
                return self._empty_results("No news articles found")

            # Step 2: Analyze impact
            logger.info(f"🧠 Step 2: Analyzing impact for {len(raw_articles)} articles...")
            analyzed_articles = self._analyze_articles(raw_articles)

            if not analyzed_articles:
                logger.warning("❌ No articles passed impact analysis")
                return self._empty_results("No high-impact news found")

            # Step 3: Rank articles
            logger.info(f"🏆 Step 3: Ranking {len(analyzed_articles)} analyzed articles...")
            ranked_articles = self._rank_articles(analyzed_articles)

            # Step 4: Translate to Thai
            logger.info(f"🇹🇭 Step 4: Translating top {len(ranked_articles)} articles to Thai...")
            thai_news = self._translate_articles(ranked_articles)

            # Step 5: Format final message
            logger.info("📱 Step 5: Formatting final message...")
            final_message = self._format_message(thai_news)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Prepare results
            results = {
                'success': True,
                'processing_time': round(processing_time, 2),
                'raw_collected': len(raw_articles),
                'analyzed_count': len(analyzed_articles),
                'final_ranked': len(ranked_articles),
                'thai_translated': len(thai_news),
                'final_message': final_message,
                'timestamp': datetime.now().isoformat(),
                'pipeline_stats': {
                    'collection_stats': self.collector_manager.get_collection_stats(),
                    'analysis_summary': self.news_analyzer.get_analysis_summary(analyzed_articles),
                    'ranking_summary': self.news_ranker.get_ranking_summary(ranked_articles),
                    'translation_summary': self.thai_translator.get_translation_summary(thai_news)
                }
            }

            self.last_run = datetime.now()
            self.last_results = results

            logger.info(f"✅ Pipeline completed successfully in {processing_time:.2f}s")
            logger.info(f"📊 Results: {results['raw_collected']} collected → {results['analyzed_count']} analyzed → {results['final_ranked']} ranked → {results['thai_translated']} translated")

            return results

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            return self._empty_results(f"Pipeline error: {str(e)}")

    def _collect_news(self) -> List[Dict]:
        """Collect news from all sources"""
        try:
            articles = self.collector_manager.collect_all_news()

            # Remove duplicates across sources
            unique_articles = self._remove_global_duplicates(articles)

            logger.info(f"📰 Collected {len(articles)} total, {len(unique_articles)} unique articles")
            return unique_articles

        except Exception as e:
            logger.error(f"Error collecting news: {e}")
            return []

    def _analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """Analyze articles for impact"""
        try:
            # Limit to reasonable number for processing
            articles_to_analyze = articles[:50]  # Max 50 articles

            analyzed = self.news_analyzer.analyze_multiple_articles(articles_to_analyze)
            logger.info(f"🧠 Analyzed {len(articles_to_analyze)} articles, {len(analyzed)} passed impact threshold")

            return analyzed

        except Exception as e:
            logger.error(f"Error analyzing articles: {e}")
            return []

    def _rank_articles(self, analyzed_articles: List[Dict]) -> List[Dict]:
        """Rank articles by importance"""
        try:
            ranked = self.news_ranker.rank_articles(analyzed_articles)
            logger.info(f"🏆 Ranked {len(ranked)} articles by importance")

            return ranked

        except Exception as e:
            logger.error(f"Error ranking articles: {e}")
            return []

    def _translate_articles(self, ranked_articles: List[Dict]) -> List[str]:
        """Translate ranked articles to Thai"""
        try:
            thai_news = self.thai_translator.translate_ranked_news(ranked_articles)
            logger.info(f"🇹🇭 Translated {len(thai_news)} articles to Thai")

            return thai_news

        except Exception as e:
            logger.error(f"Error translating articles: {e}")
            return []

    def _format_message(self, thai_news: List[str]) -> str:
        """Format final message"""
        try:
            message = self.thai_translator.format_final_message(thai_news)
            logger.info(f"📱 Final message length: {len(message)} characters")

            return message

        except Exception as e:
            logger.error(f"Error formatting message: {e}")
            return "❌ Error formatting news message"

    def _remove_global_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicates across different sources"""
        seen_titles = set()
        seen_urls = set()
        unique_articles = []

        for article in articles:
            title = article.get('title', '').lower().strip()
            url = article.get('url', '').lower().strip()

            # Skip if title or URL already seen
            if (title in seen_titles or url in seen_urls or len(title) < 10):
                continue

            seen_titles.add(title)
            seen_urls.add(url)
            unique_articles.append(article)

        return unique_articles

    def _empty_results(self, reason: str) -> Dict:
        """Return empty results when pipeline fails"""
        return {
            'success': False,
            'error': reason,
            'processing_time': 0,
            'raw_collected': 0,
            'analyzed_count': 0,
            'final_ranked': 0,
            'thai_translated': 0,
            'final_message': f"❌ {reason}\n\n*ระบบจะลองใหม่ในรอบถัดไป*",
            'timestamp': datetime.now().isoformat(),
            'pipeline_stats': {}
        }

    def get_system_status(self) -> Dict:
        """Get overall system status"""
        try:
            collector_status = self.collector_manager.get_all_status()

            return {
                'last_run': self.last_run.isoformat() if self.last_run else None,
                'collectors_count': len(self.collector_manager.collectors),
                'collectors_status': collector_status,
                'system_health': 'healthy' if self.last_results and self.last_results.get('success') else 'warning'
            }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'error': str(e),
                'system_health': 'error'
            }

    def get_last_results(self) -> Optional[Dict]:
        """Get results from last pipeline run"""
        return self.last_results

# Global pipeline instance
pipeline_instance = None

def get_pipeline() -> StockNewsPipeline:
    """Get or create pipeline instance"""
    global pipeline_instance
    if pipeline_instance is None:
        pipeline_instance = StockNewsPipeline()
    return pipeline_instance

# Quick function for testing
def test_pipeline():
    """Test the pipeline with logging"""
    try:
        pipeline = get_pipeline()
        results = pipeline.run_complete_pipeline(hours=3)

        print("\n" + "="*50)
        print("📈 PIPELINE TEST RESULTS")
        print("="*50)
        print(f"✅ Success: {results.get('success', False)}")
        print(f"📊 Collected: {results.get('raw_collected', 0)} articles")
        print(f"🧠 Analyzed: {results.get('analyzed_count', 0)} articles")
        print(f"🏆 Ranked: {results.get('final_ranked', 0)} articles")
        print(f"🇹🇭 Translated: {results.get('thai_translated', 0)} articles")
        print(f"⏱️  Processing time: {results.get('processing_time', 0)}s")
        print("\n📱 FINAL MESSAGE:")
        print("-" * 30)
        print(results.get('final_message', 'No message'))
        print("-" * 30)

        return results

    except Exception as e:
        print(f"❌ Test pipeline failed: {e}")
        return None