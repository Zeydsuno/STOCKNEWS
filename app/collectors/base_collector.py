from abc import ABC, abstractmethod
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BaseCollector(ABC):
    """Base class for all news collectors"""

    @abstractmethod
    def collect_news(self) -> List[Dict]:
        """Collect news from the source"""
        pass

    @abstractmethod
    def get_status(self) -> Dict:
        """Get collector status"""
        pass

class NewsCollectorManager:
    """Manages multiple news collectors"""

    def __init__(self):
        self.collectors = []
        self.collection_stats = {}

    def add_collector(self, collector: BaseCollector):
        """Add a news collector"""
        self.collectors.append(collector)
        logger.info(f"Added collector: {collector.__class__.__name__}")

    def collect_all_news(self) -> List[Dict]:
        """Collect news from all active collectors"""
        all_articles = []
        collection_results = {}

        for collector in self.collectors:
            try:
                collector_name = collector.__class__.__name__
                logger.info(f"Collecting from {collector_name}...")

                articles = collector.collect_news()
                all_articles.extend(articles)

                collection_results[collector_name] = {
                    'status': 'success',
                    'count': len(articles),
                    'articles': articles
                }

                logger.info(f"{collector_name}: {len(articles)} articles")

            except Exception as e:
                collector_name = collector.__class__.__name__
                logger.error(f"Error in {collector_name}: {e}")
                collection_results[collector_name] = {
                    'status': 'error',
                    'error': str(e),
                    'count': 0
                }

        self.collection_stats = collection_results
        return all_articles

    def get_collection_stats(self) -> Dict:
        """Get statistics from last collection"""
        return self.collection_stats

    def get_all_status(self) -> Dict:
        """Get status of all collectors"""
        status = {}
        for collector in self.collectors:
            collector_name = collector.__class__.__name__
            try:
                status[collector_name] = collector.get_status()
            except Exception as e:
                status[collector_name] = {'status': 'error', 'message': str(e)}
        return status