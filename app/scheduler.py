import logging
import schedule
import time
import threading
from datetime import datetime
from app.pipeline.stock_news_pipeline import get_pipeline
from app.line_bot.line_pusher import LINEPusher
from app.line_bot.message_formatter import LineMessageFormatter
from config import BROADCAST_TIMES

logger = logging.getLogger(__name__)

class NewsScheduler:
    """Schedule automated news processing and broadcasting"""

    def __init__(self):
        self.pipeline = get_pipeline()
        self.line_pusher = LINEPusher()
        self.message_formatter = LineMessageFormatter()
        self.is_running = False
        self.scheduler_thread = None

    def start_scheduler(self):
        """Start the scheduler in background thread"""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return

        # Schedule news processing
        for broadcast_time in BROADCAST_TIMES:
            schedule.every().day.at(broadcast_time).do(self._process_and_broadcast)
            logger.info(f"📅 Scheduled news processing at {broadcast_time}")

        # Add hourly collection check (optional)
        schedule.every().hour.do(self._health_check)

        # Start background thread
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()

        logger.info("🚀 News scheduler started")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("⏹️ News scheduler stopped")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("🔄 Scheduler thread started")
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)

    def _process_and_broadcast(self):
        """Process news and broadcast to LINE"""
        try:
            logger.info(f"🚀 Starting scheduled news processing at {datetime.now()}")

            # Run pipeline
            results = self.pipeline.run_complete_pipeline(hours=3)

            if results and results.get('success'):
                logger.info(f"✅ Pipeline successful: {results.get('thai_translated', 0)} articles")

                # TODO: Add LINE broadcasting here
                self._broadcast_to_line(results.get('final_message', ''))

            else:
                logger.error(f"❌ Pipeline failed: {results.get('error', 'Unknown error')}")

        except Exception as e:
            logger.error(f"❌ Scheduled processing error: {e}")

    def _broadcast_to_line(self, message: str):
        """Broadcast message to LINE"""
        try:
            if not self.line_pusher.available:
                logger.warning("[WARN] LINE Pusher not available - skipping broadcast")
                return

            # Format message for LINE
            line_message = self.message_formatter.format_text_message(message)

            # Broadcast to all users
            success = self.line_pusher.broadcast_message(line_message)

            if success:
                logger.info("[OK] Message broadcasted to LINE successfully")
            else:
                logger.error("[FAIL] Failed to broadcast to LINE")

        except Exception as e:
            logger.error(f"[ERROR] LINE broadcast error: {e}")

    def _health_check(self):
        """Hourly health check"""
        try:
            status = self.pipeline.get_system_status()
            logger.info(f"💓 Health check: {status.get('system_health', 'unknown')}")
        except Exception as e:
            logger.error(f"Health check error: {e}")

    def run_immediate(self, hours: int = 3):
        """Run pipeline immediately (for testing)"""
        logger.info(f"🚀 Running immediate pipeline for last {hours} hours")
        return self.pipeline.run_complete_pipeline(hours)

    def get_schedule_status(self):
        """Get current scheduler status"""
        next_runs = []
        for job in schedule.jobs:
            next_runs.append(str(job.next_run))

        return {
            'is_running': self.is_running,
            'scheduled_jobs': len(schedule.jobs),
            'next_runs': next_runs,
            'broadcast_times': BROADCAST_TIMES
        }

# Global scheduler instance
scheduler_instance = None

def get_scheduler() -> NewsScheduler:
    """Get or create scheduler instance"""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = NewsScheduler()
    return scheduler_instance

# Quick scheduler management
def start_news_scheduler():
    """Start the news scheduler"""
    scheduler = get_scheduler()
    scheduler.start_scheduler()

def stop_news_scheduler():
    """Stop the news scheduler"""
    scheduler = get_scheduler()
    scheduler.stop_scheduler()

def run_immediate_news():
    """Run news processing immediately for testing"""
    scheduler = get_scheduler()
    return scheduler.run_immediate()

if __name__ == "__main__":
    # Simple test runner
    print("🚀 Starting Stock News Scheduler...")
    print("📅 Scheduled times:", BROADCAST_TIMES)

    try:
        start_news_scheduler()

        print("✅ Scheduler started!")
        print("Press Ctrl+C to stop...")

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⏹️ Stopping scheduler...")
        stop_news_scheduler()
        print("✅ Scheduler stopped!")