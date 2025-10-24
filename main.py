#!/usr/bin/env python3
"""
Stock News Application - Main Entry Point
Hybrid Architecture: Free News APIs + GLM Analysis + LINE Bot
"""

import logging
import os
import sys
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.pipeline.stock_news_pipeline import test_pipeline, get_pipeline
from app.scheduler import start_news_scheduler, run_immediate_news
from config import BROADCAST_TIMES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stocknews.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner"""
    try:
        banner = """
╔═══════════════════════════════════════════════════════════════╗
║                    📈 STOCK NEWS SYSTEM                     ║
║              Hybrid AI-Powered News Analysis                ║
║                                                              ║
║  🔍 Sources: NewsAPI, RSS Feeds, Alpha Vantage              ║
║  🧠 Analysis: GLM AI Impact Scoring                          ║
║  🇹🇭 Translation: Thai Language Formatting                   ║
║  📱 Output: LINE Bot Broadcasting                            ║
╚═══════════════════════════════════════════════════════════════╝
"""
        print(banner)
    except UnicodeEncodeError:
        print("="*60)
        print("STOCK NEWS SYSTEM - Hybrid AI-Powered News Analysis")
        print("Sources: NewsAPI, RSS Feeds, Alpha Vantage")
        print("Analysis: GLM AI Impact Scoring")
        print("Translation: Thai Language Formatting")
        print("Output: LINE Bot Broadcasting")
        print("="*60)

def show_menu():
    """Show main menu"""
    try:
        menu = """
🚀 Stock News System Menu:

1. 🧪 Test Pipeline (Run once)
2. ⚡ Run Immediate News Analysis
3. 📅 Start Scheduled News Bot
4. 📊 Show System Status
5. ❌ Exit

Please select option (1-5): """
        return input(menu).strip()
    except UnicodeEncodeError:
        menu = """
Stock News System Menu:

1. Test Pipeline (Run once)
2. Run Immediate News Analysis
3. Start Scheduled News Bot
4. Show System Status
5. Exit

Please select option (1-5): """
        return input(menu).strip()

def test_pipeline_mode():
    """Test the complete pipeline"""
    print("\n" + "="*60)
    print("🧪 TESTING STOCK NEWS PIPELINE")
    print("="*60)

    try:
        results = test_pipeline()

        if results and results.get('success'):
            print("\n✅ PIPELINE TEST SUCCESSFUL!")
            print(f"📊 Statistics:")
            print(f"   • Articles collected: {results.get('raw_collected', 0)}")
            print(f"   • Articles analyzed: {results.get('analyzed_count', 0)}")
            print(f"   • Articles ranked: {results.get('final_ranked', 0)}")
            print(f"   • Articles translated: {results.get('thai_translated', 0)}")
            print(f"   • Processing time: {results.get('processing_time', 0)}s")

            # Ask if user wants to see the message
            show_msg = input("\n📱 Show the translated message? (y/n): ").strip().lower()
            if show_msg == 'y':
                print("\n" + "="*60)
                print("📱 TRANSLATED MESSAGE")
                print("="*60)
                print(results.get('final_message', 'No message'))

        else:
            print("❌ PIPELINE TEST FAILED!")
            print(f"Error: {results.get('error', 'Unknown error') if results else 'No results'}")

    except Exception as e:
        print(f"❌ Test error: {e}")

    input("\nPress Enter to continue...")

def run_immediate_mode():
    """Run immediate news analysis"""
    print("\n🚀 Running immediate news analysis...")
    print("This will process the latest news and show results.\n")

    try:
        results = run_immediate_news(hours=3)

        if results and results.get('success'):
            print(f"✅ Analysis completed!")
            print(f"📊 Found {results.get('thai_translated', 0)} high-impact news articles")
            print(f"⏱️  Processing time: {results.get('processing_time', 0)}s")

            # Preview message
            message = results.get('final_message', '')
            if len(message) > 200:
                print(f"📱 Message preview: {message[:200]}...")
            else:
                print(f"📱 Message: {message}")
        else:
            print(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Error: {e}")

    input("\nPress Enter to continue...")

def start_scheduler_mode():
    """Start the scheduled news bot"""
    print("\n📅 Starting scheduled news bot...")
    print(f"🕐 Schedule times: {', '.join(BROADCAST_TIMES)}")
    print("Press Ctrl+C to stop the scheduler.\n")

    try:
        start_news_scheduler()

        # Keep the program running
        while True:
            import time
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️ Stopping scheduler...")
        from app.scheduler import stop_news_scheduler
        stop_news_scheduler()
        print("✅ Scheduler stopped!")

    except Exception as e:
        print(f"❌ Scheduler error: {e}")

def show_system_status():
    """Show system status"""
    print("\n" + "="*60)
    print("📊 SYSTEM STATUS")
    print("="*60)

    try:
        pipeline = get_pipeline()
        status = pipeline.get_system_status()

        print(f"🏥 System Health: {status.get('system_health', 'unknown').upper()}")
        print(f"🕐 Last Run: {status.get('last_run', 'Never')}")
        print(f"📰 Collectors: {status.get('collectors_count', 0)}")

        print("\n📰 Collector Status:")
        collectors = status.get('collectors_status', {})
        for name, collector_status in collectors.items():
            print(f"   • {name}: {collector_status.get('status', 'unknown')}")

        # Last results if available
        last_results = pipeline.get_last_results()
        if last_results:
            print(f"\n📈 Last Results:")
            print(f"   • Success: {last_results.get('success', False)}")
            print(f"   • Processed: {last_results.get('raw_collected', 0)} → {last_results.get('thai_translated', 0)} articles")
            print(f"   • Processing time: {last_results.get('processing_time', 0)}s")
        else:
            print(f"\n📈 No previous results found")

    except Exception as e:
        print(f"❌ Error getting status: {e}")

    input("\nPress Enter to continue...")

def main():
    """Main application entry point"""
    print_banner()

    while True:
        try:
            choice = show_menu()

            if choice == '1':
                test_pipeline_mode()
            elif choice == '2':
                run_immediate_mode()
            elif choice == '3':
                start_scheduler_mode()
                break  # Exit if scheduler was started
            elif choice == '4':
                show_system_status()
            elif choice == '5':
                try:
                    print("\n👋 Goodbye!")
                except UnicodeEncodeError:
                    print("\nGoodbye!")
                break
            else:
                try:
                    print("❌ Invalid option. Please try again.")
                except UnicodeEncodeError:
                    print("Invalid option. Please try again.")

        except KeyboardInterrupt:
            try:
                print("\n\n👋 Goodbye!")
            except UnicodeEncodeError:
                print("\n\nGoodbye!")
            break
        except Exception as e:
            try:
                print(f"❌ Error: {e}")
            except UnicodeEncodeError:
                print(f"Error: {e}")

if __name__ == "__main__":
    main()