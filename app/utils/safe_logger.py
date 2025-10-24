"""
Safe Logger - Remove emoji for Windows compatibility
Handles emoji encoding issues on Windows console
"""

import logging
import sys

# Emoji mapping untuk safe output
EMOJI_MAP = {
    '✅': '[OK]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '🚀': '[START]',
    '📰': '[NEWS]',
    '🧠': '[ANALYSIS]',
    '🏆': '[RANKING]',
    '🇹🇭': '[TH]',
    '📱': '[MSG]',
    '🔍': '[SEARCH]',
    '📊': '[DATA]',
    '🧪': '[TEST]',
    '💡': '[TIP]',
    '🎯': '[TARGET]',
    '📈': '[UP]',
    '📉': '[DOWN]',
    '🔧': '[CONFIG]',
    '⏰': '[TIME]',
    '💰': '[PRICE]',
    '🎁': '[FEATURE]',
    '🌟': '[STAR]',
    '✨': '[SHINY]',
    '⭐': '[RATING]',
    '🔐': '[SECURE]',
    '🛠️': '[TOOL]',
    '📝': '[NOTE]',
    '📋': '[LIST]',
    '🎪': '[EVENT]',
    '🎨': '[DESIGN]',
    '🎭': '[DRAMA]',
    '🎬': '[MOVIE]',
    '🎤': '[AUDIO]',
    '🎧': '[SOUND]',
    '📞': '[CALL]',
    '📧': '[EMAIL]',
    '📡': '[SIGNAL]',
    '🌐': '[GLOBE]',
    '🗺️': '[MAP]',
    '🔗': '[LINK]',
    '🔐': '[LOCK]',
    '🔓': '[UNLOCK]',
    '💻': '[PC]',
    '📱': '[PHONE]',
    '⌚': '[WATCH]',
    '🖥️': '[DESKTOP]',
    '⌨️': '[KEYBOARD]',
    '🖱️': '[MOUSE]',
    '🖨️': '[PRINTER]',
}

def remove_emoji(text: str) -> str:
    """Remove emoji from text and replace with safe alternatives"""
    if not text:
        return text

    result = text
    for emoji, replacement in EMOJI_MAP.items():
        result = result.replace(emoji, replacement)

    # Remove any remaining emoji
    result = result.encode('ascii', 'ignore').decode('ascii')

    return result

def safe_print(text: str, **kwargs):
    """Print text safely without emoji encoding errors"""
    safe_text = remove_emoji(str(text))
    print(safe_text, **kwargs)

class SafeFormatter(logging.Formatter):
    """Custom formatter that removes emoji"""

    def format(self, record):
        # Remove emoji from the message
        record.msg = remove_emoji(str(record.msg))

        # Format the record
        formatted = super().format(record)

        return formatted

def get_safe_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Get a logger with safe emoji handling"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with safe formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create safe formatter
    formatter = SafeFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

if __name__ == "__main__":
    # Test safe logger
    logger = get_safe_logger(__name__)

    logger.info("Test message with emoji: ✅ Success! 🚀 Let's go!")
    logger.warning("Warning: ⚠️ Something might be wrong")
    logger.error("Error: ❌ Failed to process data")
    logger.info("News collected: 📰 50 articles")
    logger.info("Analysis: 🧠 Processing impact scores")
    logger.info("Ranking: 🏆 Top 10 news")
    logger.info("Translation: 🇹🇭 Thai output ready")
