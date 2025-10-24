#!/usr/bin/env python3
"""
Quick test runner for Stock News System
Run this to verify everything is working
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")

    try:
        from app.collectors.newsapi_collector import NewsAPICollector
        print("✅ NewsAPI collector imported")
    except Exception as e:
        print(f"❌ NewsAPI import error: {e}")

    try:
        from app.collectors.rss_collector import RSSCollector
        print("✅ RSS collector imported")
    except Exception as e:
        print(f"❌ RSS import error: {e}")

    try:
        from app.analysis.glm_client import GLMClient
        print("✅ GLM client imported")
    except Exception as e:
        print(f"❌ GLM client import error: {e}")

    try:
        from app.pipeline.stock_news_pipeline import get_pipeline
        print("✅ Pipeline imported")
    except Exception as e:
        print(f"❌ Pipeline import error: {e}")

def test_glm():
    """Test GLM connection"""
    print("\n🤖 Testing GLM connection...")

    try:
        from app.analysis.glm_client import test_glm_connection
        is_working = test_glm_connection()

        if is_working:
            print("✅ GLM connection working!")
        else:
            print("⚠️ GLM using mock responses - connect your GLM function")

    except Exception as e:
        print(f"❌ GLM test error: {e}")

def test_collectors():
    """Test news collectors"""
    print("\n📰 Testing news collectors...")

    try:
        from app.collectors.rss_collector import RSSCollector
        rss = RSSCollector()
        status = rss.get_feed_status()
        print(f"✅ RSS collector status: {status['working_feeds']}/{status['total_feeds']} feeds working")

    except Exception as e:
        print(f"❌ RSS collector error: {e}")

    try:
        from app.collectors.alphavantage_collector import AlphaVantageCollector
        av = AlphaVantageCollector()
        status = av.get_api_status()
        print(f"✅ Alpha Vantage status: {status['status']}")

    except Exception as e:
        print(f"❌ Alpha Vantage collector error: {e}")

def test_pipeline():
    """Test the complete pipeline"""
    print("\n🚀 Testing complete pipeline...")

    try:
        from app.pipeline.stock_news_pipeline import get_pipeline
        pipeline = get_pipeline()

        # This will use mock data since we don't want to make real API calls in tests
        print("✅ Pipeline initialized successfully")
        print("💡 Run 'python main.py' and select option 1 for full pipeline test")

    except Exception as e:
        print(f"❌ Pipeline test error: {e}")

def main():
    """Run all tests"""
    print("🧪 Stock News System - Quick Tests")
    print("=" * 50)

    test_imports()
    test_glm()
    test_collectors()
    test_pipeline()

    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print("- Check any ❌ errors above")
    print("- Run 'python main.py' for interactive testing")
    print("- Edit .env file with your API keys")
    print("- Connect GLM function in app/glm_connection.py")
    print("\n🎯 Ready when all major components show ✅")

if __name__ == "__main__":
    main()