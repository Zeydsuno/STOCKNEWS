import logging
from typing import List, Dict, Tuple
from app.analysis.glm_client import GLMClient

logger = logging.getLogger(__name__)

class NewsRanker:
    """Rank news articles by importance using GLM"""

    def __init__(self):
        self.glm_client = GLMClient()

    def rank_articles(self, analyzed_articles: List[Dict]) -> List[Dict]:
        """Rank articles by market importance"""
        if not analyzed_articles:
            return []

        # Sort by combined score first (quick ranking)
        preliminary_ranked = sorted(
            analyzed_articles,
            key=lambda x: x.get('combined_score', 0),
            reverse=True
        )

        # Take top 15 for GLM ranking (to avoid token limits)
        top_candidates = preliminary_ranked[:15]

        # Use GLM for sophisticated ranking
        final_ranked = self._glm_rank_articles(top_candidates)

        # Return top 10
        return final_ranked[:10]

    def _glm_rank_articles(self, articles: List[Dict]) -> List[Dict]:
        """Use GLM to rank articles with reasoning"""
        try:
            # Prepare ranking data
            ranking_text = self._prepare_ranking_text(articles)

            prompt = f"""
Rank these financial news articles by market importance (highest to lowest):

{ranking_text}

Ranking Criteria:
1. Impact Score: Higher scores should rank higher
2. Large-Cap Focus: News about major companies (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA)
3. Market Significance: How this affects broader market/S&P500
4. News Type Priority:
   - Earnings beats/misses: Very high priority
   - M&A announcements: Very high priority
   - Major tech/AI developments: High priority
   - Fed/macroeconomic news: High priority
   - Product launches: Medium priority
   - Analyst upgrades/downgrades: Medium priority
   - Trading updates: Lower priority

Please rank articles from 1 (most important) to 15 (least important) and provide reasoning for top 10.

Return the ranking in this format:
Rank 1: Article [X] - Most important because [brief reasoning]
Rank 2: Article [Y] - Second most important because [brief reasoning]
Rank 3: Article [Z] - Third most important because [brief reasoning]
(Continue through at least rank 10)

Focus on what moves the entire market, not just single stocks unless they're large-caps.
"""

            response = self.glm_client.call_glm(prompt, temperature=0.2)
            ranking_result = self._parse_ranking_response(response, articles)

            return ranking_result

        except Exception as e:
            logger.error(f"GLM ranking error: {e}")
            # Fallback to simple score-based ranking
            return sorted(articles, key=lambda x: x.get('combined_score', 0), reverse=True)

    def _prepare_ranking_text(self, articles: List[Dict]) -> str:
        """Prepare article text for GLM ranking"""
        ranking_lines = []

        for i, article in enumerate(articles):
            original = article.get('original_article', {})
            analysis = article.get('analysis', {})

            title = original.get('title', 'No title')
            score = analysis.get('impact_score', 0)
            combined_score = article.get('combined_score', 0)
            tickers = analysis.get('tickers', [])
            category = analysis.get('category', 'unknown')
            price_impact = analysis.get('price_impact', 'unknown')

            ranking_lines.append(
                f"Article [{i+1}]: Score {score}/{combined_score} | Tickers: {', '.join(tickers)} | "
                f"Category: {category} | Impact: {price_impact} | Title: {title}"
            )

        return "\n".join(ranking_lines)

    def _parse_ranking_response(self, response: str, articles: List[Dict]) -> List[Dict]:
        """Parse GLM ranking response"""
        try:
            lines = response.split('\n')
            ranking_mapping = {}

            for line in lines:
                if line.strip().startswith('Rank '):
                    try:
                        # Extract rank and article index
                        parts = line.split(']')
                        if len(parts) >= 2:
                            rank_part = parts[0]
                            article_index_str = rank_part.split('[')[1]
                            article_index = int(article_index_str) - 1

                            # Extract reasoning
                            reasoning_part = ' '.join(parts[1:]).replace(' - Most important because ', '').replace(' - Second most important because ', '').replace(' - Third most important because ', '')
                            reasoning_part = reasoning_part.replace(' because ', ' ', 1).strip()

                            if 0 <= article_index < len(articles):
                                # Add GLM ranking info to article
                                articles[article_index]['glm_rank'] = len(ranking_mapping) + 1
                                articles[article_index]['glm_reasoning'] = reasoning_part[:200]  # Limit reasoning length
                                ranking_mapping[article_index] = len(ranking_mapping) + 1

                    except (ValueError, IndexError) as e:
                        logger.error(f"Error parsing ranking line: {line} - {e}")
                        continue

            # Sort articles by GLM rank, fallback to combined score
            ranked_articles = []
            unranked_articles = []

            for article in articles:
                if 'glm_rank' in article:
                    ranked_articles.append(article)
                else:
                    unranked_articles.append(article)

            # Sort ranked articles by their GLM rank
            ranked_articles.sort(key=lambda x: x['glm_rank'])

            # Sort unranked articles by combined score
            unranked_articles.sort(key=lambda x: x.get('combined_score', 0), reverse=True)

            # Combine ranked and unranked
            final_ranked = ranked_articles + unranked_articles

            logger.info(f"GLM ranked {len(ranked_articles)} articles, {len(unranked_articles)} fallback")
            return final_ranked

        except Exception as e:
            logger.error(f"Error parsing ranking response: {e}")
            return sorted(articles, key=lambda x: x.get('combined_score', 0), reverse=True)

    def get_ranking_summary(self, ranked_articles: List[Dict]) -> Dict:
        """Get summary of ranking results"""
        if not ranked_articles:
            return {'total': 0, 'top_categories': {}, 'top_tickers': {}}

        top_5 = ranked_articles[:5]

        # Count categories in top 5
        categories = {}
        tickers = {}

        for article in top_5:
            category = article.get('analysis', {}).get('category', 'unknown')
            article_tickers = article.get('analysis', {}).get('tickers', [])

            categories[category] = categories.get(category, 0) + 1

            for ticker in article_tickers:
                tickers[ticker] = tickers.get(ticker, 0) + 1

        return {
            'total': len(ranked_articles),
            'top_5_categories': categories,
            'top_5_tickers': tickers,
            'average_score': sum(a.get('combined_score', 0) for a in ranked_articles) / len(ranked_articles)
        }