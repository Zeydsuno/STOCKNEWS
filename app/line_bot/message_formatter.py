"""
LINE Message Formatter
Formats stock news for LINE messages
Supports text and flex messages
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class LineMessageFormatter:
    """Format messages for LINE Bot"""

    @staticmethod
    def format_text_message(text: str) -> Dict:
        """
        Create a simple text message

        Args:
            text: Message text

        Returns:
            LINE message object
        """
        return {
            'type': 'text',
            'text': text
        }

    @staticmethod
    def format_news_summary(thai_news_lines: List[str], title: str = "Stock News Summary") -> Dict:
        """
        Format news summary as text message

        Args:
            thai_news_lines: List of formatted Thai news lines
            title: Message title

        Returns:
            LINE message object
        """
        # Join news lines with newline
        news_text = "\n".join(thai_news_lines)

        # Add title
        full_text = f"{title}\n\n{news_text}"

        # LINE has character limit, so truncate if needed
        if len(full_text) > 5000:
            full_text = full_text[:4900] + "\n... (see more in Mini App)"

        return {
            'type': 'text',
            'text': full_text,
            'wrap': True
        }

    @staticmethod
    def format_quick_reply(text: str, options: List[Dict]) -> Dict:
        """
        Create message with quick reply buttons

        Args:
            text: Main message text
            options: List of quick reply options
                [{
                    'label': 'Button text',
                    'text': 'Response text when clicked'
                }]

        Returns:
            LINE message object
        """
        quick_replies = {
            'items': [
                {
                    'type': 'action',
                    'action': {
                        'type': 'message',
                        'label': opt['label'],
                        'text': opt['text']
                    }
                }
                for opt in options
            ]
        }

        return {
            'type': 'text',
            'text': text,
            'quickReply': quick_replies
        }

    @staticmethod
    def format_news_carousel(news_items: List[Dict], limit: int = 5) -> Dict:
        """
        Create carousel message with multiple news items

        Args:
            news_items: List of news items
            limit: Max number of items to show

        Returns:
            LINE carousel message
        """
        bubbles = []

        for item in news_items[:limit]:
            title = item.get('title', '')[:40]  # Truncate title
            thai_summary = item.get('thai_summary', '')[:50]
            tickers = ', '.join(item.get('tickers', [])[:3])
            impact_score = item.get('impact_score', 0)

            bubble = {
                'type': 'bubble',
                'body': {
                    'type': 'box',
                    'layout': 'vertical',
                    'spacing': 'sm',
                    'contents': [
                        {
                            'type': 'text',
                            'text': title,
                            'weight': 'bold',
                            'size': 'sm',
                            'wrap': True
                        },
                        {
                            'type': 'text',
                            'text': thai_summary,
                            'size': 'xs',
                            'color': '#999999',
                            'wrap': True
                        },
                        {
                            'type': 'box',
                            'layout': 'horizontal',
                            'spacing': 'sm',
                            'margin': 'md',
                            'contents': [
                                {
                                    'type': 'text',
                                    'text': f'Tickers: {tickers}',
                                    'size': 'xs',
                                    'flex': 0
                                },
                                {
                                    'type': 'text',
                                    'text': f'Score: {impact_score}/10',
                                    'size': 'xs',
                                    'color': '#FF0000' if impact_score >= 8 else '#0000FF',
                                    'flex': 0
                                }
                            ]
                        }
                    ]
                },
                'footer': {
                    'type': 'box',
                    'layout': 'vertical',
                    'spacing': 'sm',
                    'contents': [
                        {
                            'type': 'button',
                            'style': 'link',
                            'height': 'sm',
                            'action': {
                                'type': 'uri',
                                'label': 'Read More',
                                'uri': item.get('url', '#')
                            }
                        }
                    ]
                }
            }

            bubbles.append(bubble)

        return {
            'type': 'carousel',
            'contents': bubbles
        }

    @staticmethod
    def format_with_mini_app_button(text: str, mini_app_url: str) -> Dict:
        """
        Create message with button linking to Mini App

        Args:
            text: Main message text
            mini_app_url: URL to Mini App

        Returns:
            LINE flex message with button
        """
        return {
            'type': 'flex',
            'altText': 'Stock News Update',
            'contents': {
                'type': 'bubble',
                'body': {
                    'type': 'box',
                    'layout': 'vertical',
                    'spacing': 'md',
                    'contents': [
                        {
                            'type': 'text',
                            'text': 'Stock News Update',
                            'weight': 'bold',
                            'size': 'lg'
                        },
                        {
                            'type': 'text',
                            'text': text,
                            'size': 'sm',
                            'wrap': True,
                            'color': '#666666'
                        }
                    ]
                },
                'footer': {
                    'type': 'box',
                    'layout': 'vertical',
                    'spacing': 'sm',
                    'contents': [
                        {
                            'type': 'button',
                            'style': 'primary',
                            'height': 'sm',
                            'action': {
                                'type': 'uri',
                                'label': 'View Dashboard',
                                'uri': mini_app_url
                            }
                        },
                        {
                            'type': 'button',
                            'style': 'link',
                            'height': 'sm',
                            'action': {
                                'type': 'message',
                                'label': 'View Summary',
                                'text': '/summary'
                            }
                        }
                    ]
                }
            }
        }

    @staticmethod
    def format_broadcast_message(thai_news_lines: List[str]) -> Dict:
        """
        Format message for broadcast to all users

        Args:
            thai_news_lines: List of formatted Thai news lines

        Returns:
            LINE message object
        """
        news_text = "\n".join(thai_news_lines)

        full_text = f"[Stock News Update]\n\n{news_text}\n\nTap 'View More' for full dashboard"

        return {
            'type': 'text',
            'text': full_text,
            'wrap': True
        }

    @staticmethod
    def format_error_message(error_text: str) -> Dict:
        """
        Create error/warning message

        Args:
            error_text: Error message

        Returns:
            LINE message object
        """
        return {
            'type': 'text',
            'text': f"[ERROR] {error_text}\n\nPlease try again later.",
            'color': '#FF0000'
        }


def test_line_formatter():
    """Test LINE Message Formatter"""
    print("Testing LINE Message Formatter...")
    print("=" * 60)

    formatter = LineMessageFormatter()

    # Test text message
    text_msg = formatter.format_text_message("Hello from Stock News Bot!")
    print("[OK] Text message formatted")

    # Test news summary
    thai_news = [
        "[1.] | \"NVDA announces partnership\" | ข่าว NVDA ลงทุน...",
        "[2.] | \"AAPL earnings beat\" | ผล earnings ของ AAPL...",
    ]
    summary_msg = formatter.format_news_summary(thai_news)
    print("[OK] News summary formatted")

    # Test quick reply
    quick_msg = formatter.format_quick_reply(
        "What would you like to see?",
        [
            {'label': 'Latest News', 'text': '/latest'},
            {'label': 'My Watchlist', 'text': '/watchlist'},
            {'label': 'Settings', 'text': '/settings'}
        ]
    )
    print("[OK] Quick reply formatted")

    # Test with mini app
    mini_app_msg = formatter.format_with_mini_app_button(
        "View our new dashboard with real-time updates!",
        "https://your-app.com/liff/dashboard"
    )
    print("[OK] Mini app message formatted")

    print("[OK] All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    test_line_formatter()
