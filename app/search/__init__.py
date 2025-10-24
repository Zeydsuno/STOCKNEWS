"""
Web Search Module
Provides web search capabilities using various providers
"""

from .duckduckgo_search import DuckDuckGoSearch
from .web_search_manager import WebSearchManager

__all__ = ['DuckDuckGoSearch', 'WebSearchManager']
