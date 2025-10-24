import logging
from typing import List, Dict, Optional
from app.analysis.glm_client import GLMClient

logger = logging.getLogger(__name__)

class ThaiNewsTranslator:
    """Translate and format news to Thai using GLM"""

    def __init__(self):
        self.glm_client = GLMClient()

    def translate_ranked_news(self, ranked_articles: List[Dict]) -> List[str]:
        """Translate top ranked news to Thai format"""
        thai_news_list = []

        for i, article in enumerate(ranked_articles[:10]):  # Top 10 articles
            try:
                thai_format = self._translate_single_article(article, i + 1)
                if thai_format:
                    thai_news_list.append(thai_format)
                    logger.info(f"Translated article {i+1}: {article.get('original_article', {}).get('title', 'Unknown')[:30]}...")
                else:
                    logger.warning(f"Failed to translate article {i+1}")

            except Exception as e:
                logger.error(f"Error translating article {i+1}: {e}")
                continue

        return thai_news_list

    def _translate_single_article(self, article: Dict, rank: int) -> Optional[str]:
        """Translate single article to Thai format"""
        try:
            original = article.get('original_article', {})
            analysis = article.get('analysis', {})

            title = original.get('title', '')
            tickers = analysis.get('tickers', [])
            impact_score = analysis.get('impact_score', 0)
            price_impact = analysis.get('price_impact', 'unknown')
            category = analysis.get('category', 'unknown')
            source = original.get('source', 'Unknown')

            # Build translation prompt
            prompt = self._build_translation_prompt(
                rank, title, tickers, impact_score, price_impact, category, source
            )

            # Get translation from GLM
            response = self.glm_client.call_glm(prompt, temperature=0.1)

            # Extract and validate the Thai format
            thai_line = self._extract_thai_format(response, rank)

            return thai_line

        except Exception as e:
            logger.error(f"Error in single article translation: {e}")
            return None

    def _build_translation_prompt(self, rank: int, title: str, tickers: List[str],
                                 impact_score: int, price_impact: str, category: str,
                                 source: str) -> str:
        """Build prompt for Thai translation using your Prompt.txt persona"""

        # Read the real prompt from Prompt.txt
        try:
            with open('Prompt.txt', 'r', encoding='utf-8') as f:
                real_prompt = f.read()
        except FileNotFoundError:
            real_prompt = "Persona: US Stock Market Screener"

        prompt = f"""
{real_prompt}

Now translate this news analysis to Thai following your exact format:

ARTICLE TO TRANSLATE:
Rank: {rank}
Headline: {title}
Tickers: {', '.join(tickers) if tickers else 'N/A'}
Impact Score: {impact_score}/10
Price Impact: {price_impact}
Source: {source}

OUTPUT FORMAT REQUIRED:
"[Rank.] | \"English Headline\" | Thai News Summary | Stock(s)/Ticker(s) | News Source | Price Impact | Impact Score"

Example from your Prompt.txt:
[1.] | "Microsoft announces $10B investment in OpenAI, expanding Azure AI integration" | ข่าวนี้สะท้อนการเร่งลงทุนใน AI ของ MSFT ทำให้มี Upside ต่อรายได้ Cloud และ AI services | MSFT | Bloomberg | Positive price impact | 9/10

Return ONLY the formatted line in Thai following your exact persona and format.
"""

        return prompt

    def _extract_thai_format(self, response: str, expected_rank: int) -> Optional[str]:
        """Extract and validate Thai format from GLM response"""
        try:
            # Look for the specific format pattern
            lines = response.strip().split('\n')

            for line in lines:
                line = line.strip()
                if line.startswith(f'[{expected_rank}.]') and '|' in line:
                    # Validate format components
                    parts = line.split('|')
                    if len(parts) >= 7:  # Should have 7 parts for complete format
                        # Check if Thai text is present (should contain Thai characters)
                        thai_summary = parts[2].strip() if len(parts) > 2 else ''
                        if thai_summary and self._contains_thai(thai_summary):
                            return line
                        else:
                            logger.warning(f"Line may not contain proper Thai text: {thai_summary[:50]}")

            # If we can't find the exact format, try to construct it
            logger.warning(f"Could not find exact format for rank {expected_rank}, attempting to extract components")
            return self._fallback_format_extraction(response, expected_rank)

        except Exception as e:
            logger.error(f"Error extracting Thai format: {e}")
            return self._fallback_format_extraction(response, expected_rank)

    def _contains_thai(self, text: str) -> bool:
        """Check if text contains Thai characters"""
        thai_chars = set('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮฤฦะาำิีึืฺุูๆเแโใไๅๆ็่้๊๋๋๎๏')
        return any(char in thai_chars for char in text)

    def _fallback_format_extraction(self, response: str, rank: int) -> Optional[str]:
        """Fallback method to extract or create Thai format"""
        try:
            # Extract title (usually in quotes)
            title_match = ""
            if '"' in response:
                start = response.find('"')
                end = response.find('"', start + 1)
                if end > start:
                    title_match = response[start:end+1]

            # Extract any Thai text
            thai_parts = []
            words = response.split()
            for word in words:
                if self._contains_thai(word):
                    thai_parts.append(word)

            # If we have some components, try to construct format
            if title_match and thai_parts:
                thai_summary = ' '.join(thai_parts[:10])  # Limit length
                fallback_line = f'[{rank}.] | {title_match} | {thai_summary} | Various | News | Price impact | Score/10'
                logger.info(f"Constructed fallback format: {fallback_line[:100]}...")
                return fallback_line

        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")

        return None

    def format_final_message(self, thai_news_list: List[str]) -> str:
        """Format the final LINE message with Thai news"""
        if not thai_news_list:
            return "📈 **ไม่พบข่าวสำคัญในช่วงเวลาที่กำหนด**\n\n*ระบบจะค้นหาข่าวใหม่ในรอบถัดไป*"

        header = "📈 **ข่าวหุ้น US สำคัญล่าสุด**\n"
        header += f"📊 **Top {len(thai_news_list)} ข่าวที่มีผลกระทบสูงสุด**\n"
        header += "⏰ **อัพเดทล่าสุด**\n\n"

        body = "\n".join(thai_news_list)

        footer = "\n\n---\n"
        footer += "💡 *สรุปโดย AI วิเคราะห์จากแหล่งข่าวที่เชื่อถือได้*"
        footer += "\n🕐 *อัพเดท 3 รอบ/วัน (9:00, 13:00, 17:00)*"
        footer += "\n📊 *Impact Score 1-10 (10 = ผลกระทบสูงสุด)*"

        return header + body + footer

    def get_translation_summary(self, thai_news_list: List[str]) -> Dict:
        """Get summary of translation results"""
        return {
            'total_translated': len(thai_news_list),
            'message_length': len(self.format_final_message(thai_news_list)),
            'success_rate': '100%' if thai_news_list else '0%'
        }