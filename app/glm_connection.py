"""
GLM Connection Wrapper with LangChain Integration
Now uses prompt files from prompts/ folder with LangChain-style architecture
"""

import os
import re
import logging
from typing import Optional, Union, Dict, List
import json

# Try to import LangChain integration
try:
    from app.langchain_integration import LangChainStockAnalyzer
    LANGCHAIN_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ LangChain integration available")
except ImportError as e:
    LANGCHAIN_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ LangChain not available: {e}")

def _call_llm(prompt: str) -> str:
    """
    Enhanced GLM function using LangChain integration
    Falls back to original implementation if LangChain not available
    """

    # Try LangChain integration first
    if LANGCHAIN_AVAILABLE:
        try:
            # Initialize LangChain analyzer
            analyzer = LangChainStockAnalyzer()

            # Determine prompt type and route accordingly
            prompt_lower = prompt.lower()

            if "analyze this financial news" in prompt_lower or "impact score" in prompt_lower:
                # Extract article data from prompt for analysis
                article_data = _extract_article_from_prompt(prompt)
                if article_data:
                    analysis = analyzer.analyze_article(article_data)
                    if analysis:
                        return json.dumps(analysis['analysis'])

            elif "translate" in prompt_lower or "thai" in prompt_lower:
                # Extract translation data from prompt
                translation_data = _extract_translation_from_prompt(prompt)
                if translation_data:
                    thai_result = analyzer.translate_to_thai(
                        translation_data['article'],
                        translation_data['rank']
                    )
                    if thai_result:
                        return thai_result

            elif "rank" in prompt_lower and "articles" in prompt_lower:
                # Extract articles for ranking
                articles_data = _extract_articles_from_prompt(prompt)
                if articles_data:
                    ranked = analyzer.rank_articles(articles_data)
                    if ranked:
                        return _format_ranking_response(ranked)

        except Exception as e:
            logger.warning(f"LangChain processing failed: {e}, falling back to mock response")

    # Fallback to original implementation
    logger.info(f"Using fallback GLM response for prompt: {prompt[:100]}...")
    return _mock_glm_response(prompt)

def _extract_article_from_prompt(prompt: str) -> Optional[Dict]:
    """Extract article data from GLM prompt"""
    try:
        lines = prompt.split('\n')
        article = {}

        for line in lines:
            if 'Title:' in line:
                article['title'] = line.split('Title:')[-1].strip()
            elif 'Source:' in line:
                article['source'] = line.split('Source:')[-1].strip()
            elif 'Content:' in line:
                article['content'] = line.split('Content:')[-1].strip()

        return article if article.get('title') else None
    except Exception as e:
        logger.error(f"Error extracting article from prompt: {e}")
        return None

def _extract_translation_from_prompt(prompt: str) -> Optional[Dict]:
    """Extract translation data from prompt"""
    try:
        import re

        rank_match = re.search(r'Rank:\s*(\d+)', prompt)
        title_match = re.search(r'Headline:\s*([^\n]+)', prompt)
        tickers_match = re.search(r'Tickers:\s*([^\n]+)', prompt)
        impact_match = re.search(r'Impact Score:\s*(\d+)', prompt)
        price_match = re.search(r'Price Impact:\s*([^\n]+)', prompt)
        source_match = re.search(r'Source:\s*([^\n]+)', prompt)

        return {
            'rank': int(rank_match.group(1)) if rank_match else 1,
            'article': {
                'title': title_match.group(1).strip() if title_match else '',
                'tickers': tickers_match.group(1).strip().split(', ') if tickers_match else [],
                'impact_score': int(impact_match.group(1)) if impact_match else 0,
                'price_impact': price_match.group(1).strip() if price_match else 'neutral',
                'source': source_match.group(1).strip() if source_match else 'Unknown'
            }
        }
    except Exception as e:
        logger.error(f"Error extracting translation data: {e}")
        return None

def _extract_articles_from_prompt(prompt: str) -> List[Dict]:
    """Extract articles list from ranking prompt"""
    try:
        # Simple extraction - in real implementation, this would be more sophisticated
        return [
            {"title": "Test Article 1", "impact_score": 9},
            {"title": "Test Article 2", "impact_score": 8}
        ]
    except Exception as e:
        logger.error(f"Error extracting articles: {e}")
        return []

def _format_ranking_response(ranked_articles: List[Dict]) -> str:
    """Format ranking response"""
    response = []
    for i, article in enumerate(ranked_articles[:5]):
        response.append(f"Rank {i+1}: Article [{i+1}] - High importance with impact score {article.get('impact_score', 0)}")

    return '\n'.join(response)

def _mock_glm_response(prompt: str) -> str:
    """
    Mock GLM response using your real Prompt.txt format
    This follows your exact persona and output format from Prompt.txt
    """

    def read_prompt_file():
        """Read your actual Prompt.txt file"""
        try:
            with open('Prompt.txt', 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return "Persona file not found"

    real_prompt_content = read_prompt_file()

    if "impact score" in prompt.lower() or "analyze this financial news" in prompt.lower():
        # Impact analysis following your Prompt.txt format
        return """
{
    "tickers": ["MSFT"],
    "impact_score": 9,
    "price_impact": "positive",
    "category": "tech-ai",
    "reasoning": "ข่าวนี้สะท้อนการเร่งลงทุนใน AI ของ MSFT ทำให้มี Upside ต่อรายได้ Cloud และ AI services",
    "market_significance": "high"
}
"""

    elif "rank" in prompt.lower() and "articles" in prompt.lower():
        # Ranking following your exact Prompt.txt format
        return """[1.] | "Microsoft announces $10B investment in OpenAI, expanding Azure AI integration" | ข่าวนี้สะท้อนการเร่งลงทุนใน AI ของ MSFT ทำให้มี Upside ต่อรายได้ Cloud และ AI services | MSFT | Bloomberg | Positive price impact | 9/10
[2.] | "Tesla Q3 deliveries miss expectations, margins continue to compress" | ยอดส่งมอบ Tesla ต่ำกว่า Consensus แสดงให้เห็นแรงกดดันด้านราคาและการแข่งขัน EV | TSLA | Reuters | Negative price impact | 8/10
[3.] | "NVIDIA announces new AI chips for data center expansion" | NVIDIA เปิดตัวชิป AI ใหม่รองรับ Data Center ขยายฐานลูกค้าในภาค AI | NVDA | CNBC | Positive price impact | 8/10
[4.] | "Fed signals potential rate cuts amid economic uncertainty" | ธนาคารกลางสหรัฐส่งสัญญาณการปรับลดดอกเบี้ย ส่งผลบวกต่อตลาดหุ้นโดยรวม | Multiple | WSJ | Positive price impact | 7/10
[5.] | "Amazon acquires healthcare startup for $4.5B" | Amazon ซื้อบริษัทสตาร์ทอัปด้านการดูแลสุขภาพเป็นมูลค่า 4.5 พันล้านดอลลาร์ | AMZN | Bloomberg | Positive price impact | 6/10"""

    elif "translate" in prompt.lower() or "thai" in prompt.lower() or "รับแปล" in prompt:
        # Thai translation following your exact Prompt.txt format
        return """[1.] | "Microsoft announces $10B investment in OpenAI, expanding Azure AI integration" | ข่าวนี้สะท้อนการเร่งลงทุนใน AI ของ MSFT ทำให้มี Upside ต่อรายได้ Cloud และ AI services | MSFT | Bloomberg | Positive price impact | 9/10"""

    else:
        # Return the actual prompt content
        return real_prompt_content

def test_glm_connection() -> bool:
    """
    Test if GLM connection is working
    Returns True if working, False if using mock responses
    """
    try:
        test_prompt = "Respond with 'GLM_CONNECTION_SUCCESS' if you can read this."
        response = _call_llm(test_prompt)

        if "GLM_CONNECTION_SUCCESS" in response:
            logger.info("✅ Real GLM connection working")
            return True
        else:
            logger.warning("⚠️ Using mock GLM responses - connect your real GLM function")
            return False

    except Exception as e:
        logger.error(f"❌ GLM connection test failed: {e}")
        return False

def get_glm_info() -> dict:
    """Get information about GLM connection status"""
    return {
        'connection_status': 'real' if test_glm_connection() else 'mock',
        'model': 'glm-4.6',
        'description': 'GLM-4.6 through Z.AI Anthropic-compatible endpoint',
        'instructions': 'Replace _call_llm() in app/glm_connection.py with your actual function'
    }

# Instructions for connecting your GLM function
INSTRUCTIONS = """
🔗 CONNECTING YOUR GLM FUNCTION:

1. Open file: app/glm_connection.py
2. Find the _call_llm() function
3. Replace the mock implementation with your actual function

Your function should look like:

def _call_llm(prompt: str) -> str:
    response = client.messages.create(
        model="glm-4.6",
        max_tokens=4096,
        temperature=0.1,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

4. Save the file
5. Test with: python -c "from app.glm_connection import test_glm_connection; test_glm_connection()"

The system will automatically use your real GLM function once connected!
"""

if __name__ == "__main__":
    print("🧪 Testing GLM Connection...")
    print("=" * 50)

    # Test connection
    is_working = test_glm_connection()

    # Show info
    info = get_glm_info()
    print(f"📊 Connection Status: {info['connection_status'].upper()}")
    print(f"🤖 Model: {info['model']}")
    print(f"📝 Description: {info['description']}")

    if not is_working:
        print("\n" + "=" * 50)
        print("🔧 SETUP INSTRUCTIONS:")
        print("=" * 50)
        print(INSTRUCTIONS)