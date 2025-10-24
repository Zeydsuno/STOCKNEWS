import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from config import NEWS_API_KEY, NEWS_TIME_RANGE_HOURS, RELIABLE_SOURCES, LARGE_CAP_STOCKS

logger = logging.getLogger(__name__)

class NewsAPICollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2"

        if not self.api_key:
            raise ValueError("NewsAPI key is required")

    def collect_news(self, hours: int = None) -> List[Dict]:
        """Main method called by pipeline - collect stock news"""
        return self.collect_stock_news(hours)

    def collect_stock_news(self, hours: int = None) -> List[Dict]:
        """Collect US stock market news from NewsAPI"""
        try:
            # Calculate time range
            time_range = hours or NEWS_TIME_RANGE_HOURS
            from_time = datetime.now() - timedelta(hours=time_range)

            # Stock-related keywords
            keywords = [
                "stock", "earnings", "market", "trading", "shares",
                "investment", "NASDAQ", "S&P500", "Dow Jones"
            ]

            # Add large-cap stocks
            stock_keywords = [ticker.lower() for ticker in LARGE_CAP_STOCKS[:20]]  # Top 20
            all_keywords = keywords + stock_keywords

            news_items = []

            # Search by different keyword combinations
            search_queries = [
                "stock market OR earnings OR trading",
                "Apple OR Microsoft OR Google OR Tesla OR NVIDIA",
                "Wall Street OR NASDAQ OR S&P",
                "investment OR shares OR dividend"
            ]

            for query in search_queries:
                try:
                    articles = self._search_articles(query, from_time)
                    news_items.extend(articles)
                    logger.info(f"Found {len(articles)} articles for query: {query}")
                except Exception as e:
                    logger.error(f"Error searching query '{query}': {e}")
                    continue

            # Remove duplicates
            unique_news = self._remove_duplicates(news_items)

            # Filter by reliable sources
            filtered_news = self._filter_by_sources(unique_news)

            logger.info(f"NewsAPI: Total collected = {len(filtered_news)} articles")
            return filtered_news[:20]  # Return top 20

        except Exception as e:
            logger.error(f"NewsAPI collection error: {e}")
            return []

    def _search_articles(self, query: str, from_time: datetime) -> List[Dict]:
        """Search articles using NewsAPI"""
        params = {
            'q': query,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_time.isoformat(),
            'pageSize': 50,
            'domains': ','.join(RELIABLE_SOURCES),
            'category': 'business'  # Focus on business news
        }

        response = requests.get(
            f"{self.base_url}/everything",
            params=params,
            headers={'X-Api-Key': self.api_key},
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get('articles', []):
            if self._is_relevant_article(article):
                articles.append(self._format_article(article))

        return articles

    def _is_relevant_article(self, article: Dict) -> bool:
        """Check if article is relevant to US stock market"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"

        # Financial indicators
        financial_keywords = [
            'stock', 'earnings', 'market', 'shares', 'price', 'nasdaq',
            'nyse', 'dow', 'sp500', 'investment', 'trading', 'dividend'
        ]

        # Check for financial keywords
        has_financial = any(keyword in content for keyword in financial_keywords)

        # Check for stock tickers
        has_tickers = any(ticker.lower() in content for ticker in LARGE_CAP_STOCKS)

        # Must have at least one financial indicator
        return has_financial or has_tickers

    def _format_article(self, article: Dict) -> Dict:
        """Format article to standard format"""
        return {
            'title': article.get('title', ''),
            'description': article.get('description', ''),
            'url': article.get('url', ''),
            'source': article.get('source', {}).get('name', 'Unknown'),
            'published_at': article.get('publishedAt', ''),
            'author': article.get('author', 'Unknown'),
            'content': article.get('content', ''),
            'collection_method': 'newsapi'
        }

    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title and URL"""
        seen_titles = set()
        seen_urls = set()
        unique_articles = []

        for article in articles:
            title = article.get('title', '').lower().strip()
            url = article.get('url', '').lower().strip()

            # Check for duplicates
            if (title not in seen_titles and
                url not in seen_urls and
                len(title) > 10):  # Skip very short titles

                seen_titles.add(title)
                seen_urls.add(url)
                unique_articles.append(article)

        return unique_articles

    def _filter_by_sources(self, articles: List[Dict]) -> List[Dict]:
        """Filter articles by reliable sources"""
        filtered = []
        for article in articles:
            source = article.get('source', '').lower()

            # Include if source is in reliable list or doesn't look like spam
            if (any(reliable in source for reliable in RELIABLE_SOURCES) or
                not any(spam_indicator in source for spam_indicator in ['blog', 'forum', 'social'])):
                filtered.append(article)

        return filtered

    def get_api_status(self) -> Dict:
        """Check API status and remaining quota"""
        try:
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params={'country': 'us', 'pageSize': 1},
                headers={'X-Api-Key': self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                return {'status': 'active', 'remaining': 'unknown'}
            else:
                return {'status': 'error', 'message': response.status_code}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}