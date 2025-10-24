"""
Flask API Server for LINE Mini App
Provides REST endpoints for news data
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from datetime import datetime, timedelta

# Import pipeline components
from app.pipeline.stock_news_pipeline import StockNewsPipeline

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for LIFF

# Initialize pipeline
pipeline = StockNewsPipeline()

# In-memory cache (replace with Redis in production)
news_cache = {
    'last_update': None,
    'news': []
}

@app.route('/')
def home():
    """API home"""
    return jsonify({
        'service': 'Stock News API',
        'version': '1.0',
        'endpoints': {
            '/api/news/latest': 'Get latest news',
            '/api/news/search': 'Search news by keyword',
            '/api/news/ticker/<symbol>': 'Get news for specific ticker',
            '/api/status': 'Get system status'
        }
    })

@app.route('/api/news/latest')
def get_latest_news():
    """Get latest news"""
    try:
        # Check cache (refresh every 15 minutes)
        now = datetime.now()
        if (news_cache['last_update'] and
            (now - news_cache['last_update']) < timedelta(minutes=15) and
            news_cache['news']):
            logger.info("[CACHE] Returning cached news")
            return jsonify({
                'success': True,
                'cached': True,
                'count': len(news_cache['news']),
                'news': news_cache['news']
            })

        # Run pipeline
        logger.info("[API] Running news pipeline...")
        results = pipeline.run_complete_pipeline(hours=3)

        if results.get('success'):
            # Update cache
            news_cache['last_update'] = now
            news_cache['news'] = results.get('analyzed_articles', [])

            return jsonify({
                'success': True,
                'cached': False,
                'count': len(news_cache['news']),
                'news': news_cache['news'],
                'stats': {
                    'collected': results.get('raw_collected', 0),
                    'analyzed': results.get('analyzed_count', 0),
                    'processing_time': results.get('processing_time', 0)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Pipeline failed')
            }), 500

    except Exception as e:
        logger.error(f"[ERROR] API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news/search')
def search_news():
    """Search news by keyword or ticker"""
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400

        # Search in cache
        if not news_cache['news']:
            return jsonify({
                'success': True,
                'count': 0,
                'news': []
            })

        # Filter news
        filtered = []
        for article in news_cache['news']:
            title = article.get('original_article', {}).get('title', '').lower()
            tickers = [t.lower() for t in article.get('analysis', {}).get('tickers', [])]

            if query in title or query in ' '.join(tickers):
                filtered.append(article)

        return jsonify({
            'success': True,
            'query': query,
            'count': len(filtered),
            'news': filtered
        })

    except Exception as e:
        logger.error(f"[ERROR] Search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news/ticker/<symbol>')
def get_ticker_news(symbol):
    """Get news for specific ticker"""
    try:
        symbol = symbol.upper()

        if not news_cache['news']:
            return jsonify({
                'success': True,
                'ticker': symbol,
                'count': 0,
                'news': []
            })

        # Filter by ticker
        ticker_news = []
        for article in news_cache['news']:
            tickers = [t.upper() for t in article.get('analysis', {}).get('tickers', [])]
            if symbol in tickers:
                ticker_news.append(article)

        return jsonify({
            'success': True,
            'ticker': symbol,
            'count': len(ticker_news),
            'news': ticker_news
        })

    except Exception as e:
        logger.error(f"[ERROR] Ticker news error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news/filter')
def filter_news():
    """Filter news by multiple criteria"""
    try:
        # Get filter parameters
        min_impact = int(request.args.get('min_impact', 0))
        max_impact = int(request.args.get('max_impact', 10))
        price_impact = request.args.get('price_impact', '').lower()  # positive/negative/neutral
        category = request.args.get('category', '').lower()

        if not news_cache['news']:
            return jsonify({
                'success': True,
                'count': 0,
                'news': []
            })

        # Apply filters
        filtered = news_cache['news']

        # Impact score filter
        filtered = [a for a in filtered
                   if min_impact <= a.get('analysis', {}).get('impact_score', 0) <= max_impact]

        # Price impact filter
        if price_impact:
            filtered = [a for a in filtered
                       if a.get('analysis', {}).get('price_impact', '').lower() == price_impact]

        # Category filter
        if category:
            filtered = [a for a in filtered
                       if a.get('analysis', {}).get('category', '').lower() == category]

        return jsonify({
            'success': True,
            'filters': {
                'min_impact': min_impact,
                'max_impact': max_impact,
                'price_impact': price_impact,
                'category': category
            },
            'count': len(filtered),
            'news': filtered
        })

    except Exception as e:
        logger.error(f"[ERROR] Filter error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """Get system status"""
    try:
        return jsonify({
            'success': True,
            'status': 'online',
            'cache': {
                'last_update': news_cache['last_update'].isoformat() if news_cache['last_update'] else None,
                'news_count': len(news_cache['news'])
            },
            'pipeline': pipeline.get_system_status()
        })

    except Exception as e:
        logger.error(f"[ERROR] Status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh')
def refresh_news():
    """Force refresh news (manually trigger pipeline)"""
    try:
        logger.info("[API] Manual refresh triggered...")
        results = pipeline.run_complete_pipeline(hours=3)

        if results.get('success'):
            # Update cache
            news_cache['last_update'] = datetime.now()
            news_cache['news'] = results.get('analyzed_articles', [])

            return jsonify({
                'success': True,
                'message': 'News refreshed successfully',
                'count': len(news_cache['news']),
                'stats': {
                    'collected': results.get('raw_collected', 0),
                    'analyzed': results.get('analyzed_count', 0),
                    'processing_time': results.get('processing_time', 0)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': results.get('error', 'Pipeline failed')
            }), 500

    except Exception as e:
        logger.error(f"[ERROR] Refresh error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_api_server(host='0.0.0.0', port=5000, debug=False):
    """Run Flask API server"""
    logger.info(f"[START] Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run server
    run_api_server(debug=True)
