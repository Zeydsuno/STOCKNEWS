import requests
import os
from datetime import datetime
from typing import List, Dict
import logging
from config import ALPHA_VANTAGE_KEY, LARGE_CAP_STOCKS

logger = logging.getLogger(__name__)

class AlphaVantageCollector:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_KEY')
        self.base_url = "https://www.alphavantage.co/query"

        if not self.api_key or self.api_key == 'YOUR_ALPHA_VANTAGE_KEY':
            logger.warning("Alpha Vantage API key not configured - using demo mode")
            self.demo_mode = True
        else:
            self.demo_mode = False

    def collect_news(self, hours: int = None) -> List[Dict]:
        """Main method called by pipeline - collect market news"""
        return self.collect_market_news(hours)

    def collect_market_news(self, hours: int = None) -> List[Dict]:
        """Collect financial news from Alpha Vantage"""
        if self.demo_mode:
            return self._get_demo_news()

        try:
            # Get general market news
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'limit': 50,
                'sort': 'LATEST'
            }

            response = requests.get(self.base_url, params=params, timeout=20)
            response.raise_for_status()
            data = response.json()

            # Extract articles from response
            articles = []
            feed_data = data.get('feed', [])

            for item in feed_data:
                if self._is_relevant_news(item):
                    article = self._format_alpha_vantage_article(item)
                    if article:
                        articles.append(article)

            logger.info(f"Alpha Vantage: Found {len(articles)} relevant articles")
            return articles

        except Exception as e:
            logger.error(f"Alpha Vantage collection error: {e}")
            return []

    def collect_ticker_news(self, tickers: List[str] = None) -> List[Dict]:
        """Collect news for specific tickers"""
        if self.demo_mode:
            return self._get_demo_ticker_news()

        tickers = tickers or LARGE_CAP_STOCKS[:10]  # Top 10 by default
        all_articles = []

        for ticker in tickers:
            try:
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'apikey': self.api_key,
                    'tickers': ticker,
                    'limit': 10,
                    'sort': 'LATEST'
                }

                response = requests.get(self.base_url, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()

                feed_data = data.get('feed', [])
                for item in feed_data:
                    article = self._format_alpha_vantage_article(item)
                    if article:
                        article['ticker_focus'] = ticker
                        all_articles.append(article)

                logger.info(f"Alpha Vantage {ticker}: {len(feed_data)} articles")

                # Small delay to avoid rate limits
                import time
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Alpha Vantage ticker {ticker} error: {e}")
                continue

        return all_articles

    def _is_relevant_news(self, item: Dict) -> bool:
        """Check if news item is relevant to US stock market"""
        title = item.get('title', '').lower()
        summary = item.get('summary', '').lower()

        # Check for financial relevance
        financial_keywords = [
            'stock', 'market', 'earnings', 'trading', 'investment',
            'shares', 'price', 'nasdaq', 'nyse', 'dow', 'sp500'
        ]

        content = f"{title} {summary}"
        has_financial = any(keyword in content for keyword in financial_keywords)

        # Check sentiment score threshold (only include moderate to high impact news)
        sentiment_score = item.get('overall_sentiment_score', 0)
        if abs(sentiment_score) < 0.1:  # Skip very neutral news
            return False

        return has_financial

    def _format_alpha_vantage_article(self, item: Dict) -> Dict:
        """Format Alpha Vantage article to standard format"""
        try:
            # Convert timestamp
            time_published = item.get('time_published', '')
            if time_published:
                # Alpha Vantage format: YYYYMMDDTHHMMSS
                dt = datetime.strptime(time_published, '%Y%m%dT%H%M%S')
                published_at = dt.isoformat()
            else:
                published_at = datetime.now().isoformat()

            # Extract tickers from ticker_sentiment
            tickers = []
            ticker_data = item.get('ticker_sentiment', [])
            for ticker_info in ticker_data:
                ticker = ticker_info.get('ticker', '')
                if ticker and ticker in LARGE_CAP_STOCKS:
                    tickers.append(ticker)

            return {
                'title': item.get('title', ''),
                'description': item.get('summary', ''),
                'url': item.get('url', ''),
                'source': 'Alpha Vantage',
                'published_at': published_at,
                'author': item.get('source', 'Alpha Vantage'),
                'content': item.get('summary', ''),
                'collection_method': 'alphavantage',
                'tickers': tickers,
                'sentiment_score': item.get('overall_sentiment_score', 0),
                'sentiment_label': item.get('overall_sentiment_label', 'neutral')
            }

        except Exception as e:
            logger.error(f"Error formatting Alpha Vantage article: {e}")
            return None

    def _get_demo_news(self) -> List[Dict]:
        """Demo news for testing without API key"""
        return [
            {
                'title': 'Major Tech Stocks Rally on AI Optimism',
                'description': 'Technology giants led market gains as investors cheered advances in artificial intelligence.',
                'url': 'https://example.com/news1',
                'source': 'Alpha Vantage Demo',
                'published_at': datetime.now().isoformat(),
                'author': 'Demo Mode',
                'content': 'Demo content for testing',
                'collection_method': 'alphavantage_demo',
                'tickers': ['AAPL', 'MSFT', 'GOOGL'],
                'sentiment_score': 0.3,
                'sentiment_label': 'positive'
            },
            {
                'title': 'Fed Signals Potential Rate Changes',
                'description': 'Federal Reserve officials hint at future monetary policy adjustments.',
                'url': 'https://example.com/news2',
                'source': 'Alpha Vantage Demo',
                'published_at': datetime.now().isoformat(),
                'author': 'Demo Mode',
                'content': 'Demo content for testing',
                'collection_method': 'alphavantage_demo',
                'tickers': [],
                'sentiment_score': -0.1,
                'sentiment_label': 'negative'
            }
        ]

    def _get_demo_ticker_news(self) -> List[Dict]:
        """Demo ticker-specific news"""
        return [
            {
                'title': f'{ticker} Reports Strong Quarterly Results',
                'description': f'Company {ticker} exceeded analyst expectations with strong earnings growth.',
                'url': 'https://example.com/ticker-news',
                'source': 'Alpha Vantage Demo',
                'published_at': datetime.now().isoformat(),
                'author': 'Demo Mode',
                'content': f'Demo ticker news for {ticker}',
                'collection_method': 'alphavantage_demo',
                'ticker_focus': ticker,
                'tickers': [ticker],
                'sentiment_score': 0.4,
                'sentiment_label': 'positive'
            }
            for ticker in ['AAPL', 'MSFT', 'GOOGL']
        ]

    def get_api_status(self) -> Dict:
        """Check Alpha Vantage API status"""
        if self.demo_mode:
            return {'status': 'demo_mode', 'message': 'Using demo data'}

        try:
            # Simple test call
            params = {
                'function': 'NEWS_SENTIMENT',
                'apikey': self.api_key,
                'limit': 1
            }

            response = requests.get(self.base_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'Note' in data:
                    return {'status': 'rate_limited', 'message': 'API rate limit exceeded'}
                elif 'Error Message' in data:
                    return {'status': 'error', 'message': data['Error Message']}
                else:
                    return {'status': 'active', 'message': 'API working'}
            else:
                return {'status': 'error', 'message': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'status': 'error', 'message': str(e)}