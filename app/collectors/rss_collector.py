import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from config import NEWS_TIME_RANGE_HOURS

logger = logging.getLogger(__name__)

class RSSCollector:
    def __init__(self):
        self.rss_feeds = [
            # Yahoo Finance RSS feeds
            'https://finance.yahoo.com/rss/',
            'https://finance.yahoo.com/news/rssindex/',
            'https://finance.yahoo.com/tech/rss/',
            'https://finance.yahoo.com/sector-technology/rss/',

            # MarketWatch RSS
            'https://feeds.feedburner.com/marketwatch/stocks',
            'https://feeds.feedburner.com/marketwatch/topstories',

            # Bloomberg RSS
            'https://feeds.bloomberg.com/markets/news.rss',
            'https://feeds.bloomberg.com/technology/news.rss',

            # Google News - Business & Finance
            'https://news.google.com/rss/topics/CAAqJggKIiBDQklTR3JBR2l3QlRNd2hCSFFHbDlBUUFC',

            # Reuters Business News
            'https://www.reuters.com/rssFeed/businessNews',
            'https://www.reuters.com/rssFeed/marketsNews',
        ]

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def collect_news(self, hours: int = None) -> List[Dict]:
        """Main method called by pipeline - collect RSS news"""
        return self.collect_all_feeds(hours)

    def collect_all_feeds(self, hours: int = None) -> List[Dict]:
        """Collect news from all RSS feeds"""
        all_articles = []

        for feed_url in self.rss_feeds:
            try:
                articles = self._collect_from_feed(feed_url)
                all_articles.extend(articles)
                logger.info(f"RSS {feed_url}: Found {len(articles)} articles")
            except Exception as e:
                logger.error(f"RSS feed error {feed_url}: {e}")
                continue

        # Filter by time and remove duplicates
        recent_articles = self._filter_by_time(all_articles, hours)
        unique_articles = self._remove_duplicates(recent_articles)

        logger.info(f"RSS: Total collected = {len(unique_articles)} articles")
        return unique_articles

    def _collect_from_feed(self, feed_url: str) -> List[Dict]:
        """Collect articles from a single RSS feed"""
        try:
            # Make request with headers
            response = requests.get(feed_url, headers=self.headers, timeout=15)
            response.raise_for_status()

            # Parse RSS feed
            feed = feedparser.parse(response.content)

            articles = []
            for entry in feed.entries:
                article = self._format_rss_entry(entry, feed_url)
                if article and self._is_financial_article(article):
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error collecting from {feed_url}: {e}")
            return []

    def _format_rss_entry(self, entry, feed_url: str) -> Dict:
        """Format RSS entry to standard format"""
        try:
            published = entry.get('published_parsed')
            if published:
                published_dt = datetime(*published[:6])
            else:
                published_dt = datetime.now()

            # Extract source name from feed URL
            source = self._extract_source_name(feed_url)

            return {
                'title': entry.get('title', ''),
                'description': entry.get('description', ''),
                'url': entry.get('link', ''),
                'source': source,
                'published_at': published_dt.isoformat(),
                'author': entry.get('author', source),
                'content': entry.get('summary', entry.get('description', '')),
                'collection_method': 'rss'
            }

        except Exception as e:
            logger.error(f"Error formatting RSS entry: {e}")
            return None

    def _extract_source_name(self, feed_url: str) -> str:
        """Extract source name from feed URL"""
        url_mapping = {
            'yahoo': 'Yahoo Finance',
            'bloomberg': 'Bloomberg',
            'reuters': 'Reuters',
            'marketwatch': 'MarketWatch',
            'google': 'Google News'
        }

        for key, name in url_mapping.items():
            if key in feed_url.lower():
                return name

        return 'RSS Feed'

    def _is_financial_article(self, article: Dict) -> bool:
        """Check if article is relevant to finance"""
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}"

        financial_keywords = [
            'stock', 'earnings', 'market', 'shares', 'price', 'trading',
            'investment', 'nasdaq', 'nyse', 'dow', 'sp500', 'wall street',
            'dividend', 'etf', 'mutual fund', 'portfolio'
        ]

        return any(keyword in content for keyword in financial_keywords)

    def _filter_by_time(self, articles: List[Dict], hours: int = None) -> List[Dict]:
        """Filter articles by publication time"""
        time_range = hours or NEWS_TIME_RANGE_HOURS
        cutoff_time = datetime.now() - timedelta(hours=time_range)
        recent_articles = []

        for article in articles:
            try:
                published_str = article.get('published_at', '')
                if not published_str:
                    continue

                published_dt = datetime.fromisoformat(published_str.replace('Z', '+00:00'))

                if published_dt >= cutoff_time:
                    recent_articles.append(article)

            except Exception as e:
                logger.error(f"Error parsing date: {e}")
                # If we can't parse date, include article anyway (it might be recent)
                recent_articles.append(article)

        return recent_articles

    def _remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles"""
        seen_titles = set()
        seen_urls = set()
        unique_articles = []

        for article in articles:
            title = article.get('title', '').lower().strip()
            url = article.get('url', '').lower().strip()

            if (title not in seen_titles and
                url not in seen_urls and
                len(title) > 10):  # Skip very short titles

                seen_titles.add(title)
                seen_urls.add(url)
                unique_articles.append(article)

        return unique_articles

    def get_feed_status(self) -> Dict:
        """Check status of RSS feeds"""
        status = {}
        working_feeds = 0

        for feed_url in self.rss_feeds:
            try:
                response = requests.get(feed_url, headers=self.headers, timeout=5)
                if response.status_code == 200:
                    status[feed_url] = 'active'
                    working_feeds += 1
                else:
                    status[feed_url] = f'error_{response.status_code}'
            except Exception as e:
                status[feed_url] = f'error_{str(e)}'

        return {
            'total_feeds': len(self.rss_feeds),
            'working_feeds': working_feeds,
            'details': status
        }