import json
import logging
from typing import Dict, Optional
import os
from config import GLM_API_KEY, GLM_MODEL

logger = logging.getLogger(__name__)

# Import your existing GLM client
try:
    from app.glm_connection import _call_llm as your_glm_function
    GLM_AVAILABLE = True
except ImportError:
    logger.warning("Your GLM function not found, using fallback")
    GLM_AVAILABLE = False

class GLMClient:
    """Client for GLM API calls using your existing _call_llm function"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or GLM_API_KEY
        self.model = GLM_MODEL

        if not GLM_AVAILABLE:
            logger.warning("⚠️ GLM not available - using mock responses")
            self.mock_mode = True
        else:
            self.mock_mode = False

    def call_glm(self, prompt: str, temperature: float = 0.1) -> str:
        """Call GLM API using your existing function"""
        if self.mock_mode:
            return self._mock_response(prompt)

        try:
            # Use your existing _call_llm function
            response = your_glm_function(prompt)
            return str(response) if response else ""

        except Exception as e:
            logger.error(f"GLM API call failed: {e}")
            # Fallback to mock response
            return self._mock_response(prompt)

    def _mock_response(self, prompt: str) -> str:
        """Mock response when GLM is not available"""
        if "impact score" in prompt.lower():
            return json.dumps({
                "tickers": ["AAPL", "MSFT"],
                "impact_score": 7,
                "price_impact": "positive",
                "category": "tech-ai",
                "reasoning": "Mock: Tech innovation drives positive sentiment",
                "market_significance": "high"
            })

        elif "translate" in prompt.lower() or "thai" in prompt.lower():
            return """[1.] | "Tech innovation drives market growth" | นวัตกรรมเทคโนโลยีขับเคลื่อนการเติบโตของตลาดหุ้น สะท้อนความหวังในภาคเทคโนโลยี | AAPL, MSFT | Mock Source | Positive price impact | 7/10"""

        else:
            return "Mock GLM response - please configure proper GLM connection"

def test_glm_connection():
    """Test GLM connection with simple prompt"""
    try:
        glm_client = GLMClient()

        test_prompt = "Respond with 'GLM is working' if you can read this."
        response = glm_client.call_glm(test_prompt)

        if "working" in response.lower():
            logger.info("✅ GLM connection successful")
            return True
        else:
            logger.warning(f"⚠️ Unexpected GLM response: {response}")
            return False

    except Exception as e:
        logger.error(f"❌ GLM connection failed: {e}")
        return False