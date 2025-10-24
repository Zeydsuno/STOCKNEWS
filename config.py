import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'YOUR_NEWSAPI_KEY')
ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'YOUR_ALPHA_VANTAGE_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YOUR_LINE_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', 'YOUR_LINE_SECRET')

# GLM Configuration
GLM_API_KEY = os.getenv('GLM_API_KEY')
GLM_MODEL = "glm-4.6"

# Mistral AI Configuration
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
MISTRAL_MODEL = os.getenv('MISTRAL_MODEL', 'mistral-large-latest')
MISTRAL_ENABLE_SEARCH = os.getenv('MISTRAL_ENABLE_SEARCH', 'True').lower() == 'true'

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///stocknews.db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')

# News Collection Settings
NEWS_TIME_RANGE_HOURS = 3
MAX_ARTICLES_PER_SOURCE = 20
MIN_IMPACT_SCORE = 5  # Only analyze articles with potential impact >= 5

# Large Cap Stocks (Priority List)
LARGE_CAP_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA',
    'JPM', 'V', 'PG', 'JNJ', 'WMT', 'UNH', 'HD', 'MA', 'BAC', 'XOM',
    'CVX', 'LLY', 'ABBV', 'PFE', 'KO', 'PEP', 'TMO', 'AVGO', 'COST',
    'CRM', 'ACN', 'NKE', 'ADBE', 'TXN', 'NFLX', 'CMCSA', 'INTC',
    'AMD', 'HD', 'PYPL', 'DIS', 'VZ', 'CSCO', 'CRM'
]

# Reliable News Sources (Priority)
RELIABLE_SOURCES = [
    'bloomberg.com', 'reuters.com', 'wsj.com', 'cnbc.com',
    'yahoo.com', 'marketwatch.com', 'barrons.com', 'seekingalpha.com',
    'fool.com', 'investopedia.com', 'benzinga.com'
]

# Scheduling
BROADCAST_TIMES = ['09:00', '13:00', '17:00']  # 9AM, 1PM, 5PM
NEWS_COLLECTION_INTERVAL = 15  # Every 15 minutes

# Output Format (from Prompt.txt)
OUTPUT_FORMAT = "[Rank] | \"Headline\" | Thai Summary | Stock(s)/Ticker(s) | News Source | Price Impact | Impact Score"

# Web Search Configuration
WEB_SEARCH_ENABLED = True
WEB_SEARCH_PROVIDER = 'duckduckgo'  # Free forever!
WEB_SEARCH_MAX_RESULTS = 5
WEB_SEARCH_CACHE_TTL = 3600  # 1 hour in seconds

# Uncertainty Detection Thresholds
UNCERTAINTY_THRESHOLD = 0.7  # < 70% confidence = uncertain
HIGH_IMPACT_THRESHOLD = 8    # >= 8 = high impact news (need accuracy)
MIN_TICKERS_REQUIRED = 1     # Minimum tickers to extract

# Web Search Triggers (when to use web search)
SEARCH_ON_UNCERTAINTY = True      # Search when AI confidence < threshold
SEARCH_ON_HIGH_IMPACT = True      # Search for high-impact news to verify
SEARCH_ON_MISSING_TICKERS = True  # Search when tickers not found