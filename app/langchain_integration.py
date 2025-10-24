"""
LangChain Integration for Stock News System
Uses prompt files from prompts/ folder with LangChain
"""

import os
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LangChainStockAnalyzer:
    """Stock News Analysis using LangChain and file-based prompts"""

    def __init__(self, llm_provider="openai", api_key=None):
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.prompts_dir = Path("prompts")

        # Load prompts from files
        self.system_prompt = self._load_prompt("system_prompt.txt")
        self.analysis_prompt = self._load_prompt("analysis_prompt.txt")
        self.translation_prompt = self._load_prompt("translation_prompt.txt")
        self.ranking_prompt = self._load_prompt("ranking_prompt.txt")

        logger.info(f"✅ Loaded {len([self.system_prompt, self.analysis_prompt, self.translation_prompt, self.ranking_prompt])} prompt files")

    def _load_prompt(self, filename: str) -> str:
        """Load prompt from prompts folder"""
        try:
            prompt_path = self.prompts_dir / filename
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"📝 Loaded prompt: {filename}")
                return content
            else:
                logger.warning(f"⚠️ Prompt file not found: {filename}")
                return f"Prompt file {filename} not found"
        except Exception as e:
            logger.error(f"❌ Error loading prompt {filename}: {e}")
            return f"Error loading prompt: {filename}"

    def analyze_article(self, article: Dict) -> Optional[Dict]:
        """Analyze single article using LangChain-style prompt"""
        try:
            title = article.get('title', '')
            content = article.get('content', '')[:1000]
            source = article.get('source', '')

            # Format prompt with article data
            formatted_prompt = self.analysis_prompt.format(
                title=title,
                content=content,
                source=source
            )

            # Add system context
            full_prompt = f"{self.system_prompt}\n\n{formatted_prompt}"

            # For now, return mock analysis (replace with actual LLM call later)
            return self._mock_analysis(title, source)

        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return None

    def translate_to_thai(self, article_data: Dict, rank: int) -> Optional[str]:
        """Translate article to Thai using LangChain prompt"""
        try:
            title = article_data.get('title', '')
            tickers = ', '.join(article_data.get('tickers', []))
            impact_score = article_data.get('impact_score', 0)
            price_impact = article_data.get('price_impact', 'neutral')
            source = article_data.get('source', 'Unknown')

            # Format translation prompt
            formatted_prompt = self.translation_prompt.format(
                rank=rank,
                title=title,
                tickers=tickers,
                impact_score=impact_score,
                price_impact=price_impact,
                source=source
            )

            # Return mock translation (replace with actual LLM call later)
            return f'[{rank}.] | "{title}" | ข่าวนี้สะท้อนการวิเคราะห์ตลาดหุ้นสหรัฐ | {tickers} | {source} | {price_impact} price impact | {impact_score}/10'

        except Exception as e:
            logger.error(f"Error translating article: {e}")
            return None

    def rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Rank articles by importance"""
        try:
            # Format articles for ranking prompt
            articles_text = "\n".join([
                f"Article {i+1}: {article.get('title', 'No title')} (Impact: {article.get('impact_score', 0)})"
                for i, article in enumerate(articles)
            ])

            formatted_prompt = self.ranking_prompt.format(articles=articles_text)
            full_prompt = f"{self.system_prompt}\n\n{formatted_prompt}"

            # Return ranked articles (mock implementation)
            return sorted(articles, key=lambda x: x.get('impact_score', 0), reverse=True)

        except Exception as e:
            logger.error(f"Error ranking articles: {e}")
            return articles

    def _mock_analysis(self, title: str, source: str) -> Dict:
        """Mock analysis for testing"""
        return {
            "original_article": {"title": title, "source": source},
            "analysis": {
                "tickers": ["MSFT", "AAPL"],
                "impact_score": 8,
                "price_impact": "positive",
                "category": "tech-ai",
                "reasoning": "Mock analysis based on title patterns",
                "market_significance": "high"
            }
        }

    def get_prompt_info(self) -> Dict:
        """Get information about loaded prompts"""
        return {
            "prompts_directory": str(self.prompts_dir),
            "system_prompt_loaded": bool(self.system_prompt and "Prompt file" not in self.system_prompt),
            "analysis_prompt_loaded": bool(self.analysis_prompt and "Prompt file" not in self.analysis_prompt),
            "translation_prompt_loaded": bool(self.translation_prompt and "Prompt file" not in self.translation_prompt),
            "ranking_prompt_loaded": bool(self.ranking_prompt and "Prompt file" not in self.ranking_prompt),
            "llm_provider": self.llm_provider,
            "ready_for_llm": bool(self.api_key)
        }

def test_langchain_integration():
    """Test LangChain integration"""
    def safe_print(text):
        try:
            print(text)
        except UnicodeEncodeError:
            print(text.encode('ascii', errors='ignore').decode('ascii'))

    safe_print("Testing LangChain Integration...")
    safe_print("=" * 50)

    analyzer = LangChainStockAnalyzer()

    # Show prompt info
    info = analyzer.get_prompt_info()
    safe_print(f"Prompts Directory: {info['prompts_directory']}")
    safe_print(f"LLM Provider: {info['llm_provider']}")
    safe_print(f"System Prompt: {'Loaded' if info['system_prompt_loaded'] else 'Not found'}")
    safe_print(f"Analysis Prompt: {'Loaded' if info['analysis_prompt_loaded'] else 'Not found'}")
    safe_print(f"Translation Prompt: {'Loaded' if info['translation_prompt_loaded'] else 'Not found'}")
    safe_print(f"Ranking Prompt: {'Loaded' if info['ranking_prompt_loaded'] else 'Not found'}")

    # Test article analysis
    test_article = {
        "title": "Microsoft announces $10B investment in OpenAI",
        "source": "Bloomberg",
        "content": "Microsoft today announced a significant investment..."
    }

    safe_print("\nTesting Article Analysis...")
    analysis = analyzer.analyze_article(test_article)
    if analysis:
        safe_print(f"Analysis successful: Impact Score {analysis['analysis']['impact_score']}")
    else:
        safe_print("Analysis failed")

    safe_print("\nTo connect real LLM:")
    safe_print("1. Set OPENAI_API_KEY environment variable")
    safe_print("2. Replace mock functions with actual LangChain LLM calls")
    safe_print("=" * 50)

if __name__ == "__main__":
    test_langchain_integration()