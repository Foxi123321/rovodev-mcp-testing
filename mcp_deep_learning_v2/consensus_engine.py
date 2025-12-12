"""
Consensus Engine - Merges analysis from DeepSeek and Qwen
Computes agreement scores and creates unified understanding
"""

import logging
import difflib
from typing import Dict, Any, Optional
import re

from config import CONSENSUS_THRESHOLD, HIGH_CONFIDENCE_THRESHOLD

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """Merge and validate results from dual AI analysis"""
    
    @staticmethod
    def compute_text_similarity(text1: str, text2: str) -> float:
        """Compute similarity between two text strings (0-1)"""
        if not text1 or not text2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        matcher = difflib.SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    @staticmethod
    def extract_key_points(text: str) -> set:
        """Extract key points/concepts from analysis text"""
        # Simple keyword extraction
        # Remove common words and extract meaningful terms
        text = text.lower()
        
        # Common code analysis terms to look for
        keywords = {
            'function', 'method', 'class', 'variable', 'loop', 'condition',
            'error', 'bug', 'security', 'performance', 'optimization',
            'database', 'query', 'api', 'authentication', 'validation',
            'async', 'await', 'promise', 'callback', 'return', 'parameter',
            'complexity', 'o(n)', 'o(1)', 'o(log n)', 'recursive', 'iterative'
        }
        
        found_keywords = set()
        for keyword in keywords:
            if keyword in text:
                found_keywords.add(keyword)
        
        return found_keywords
    
    @staticmethod
    def compute_semantic_agreement(primary: str, secondary: str) -> float:
        """
        Compute semantic agreement between two analyses
        Returns score 0-1
        """
        # Text similarity
        text_sim = ConsensusEngine.compute_text_similarity(primary, secondary)
        
        # Keyword overlap
        primary_keywords = ConsensusEngine.extract_key_points(primary)
        secondary_keywords = ConsensusEngine.extract_key_points(secondary)
        
        if not primary_keywords and not secondary_keywords:
            keyword_overlap = 1.0
        elif not primary_keywords or not secondary_keywords:
            keyword_overlap = 0.0
        else:
            intersection = len(primary_keywords & secondary_keywords)
            union = len(primary_keywords | secondary_keywords)
            keyword_overlap = intersection / union if union > 0 else 0.0
        
        # Weighted combination
        agreement = (text_sim * 0.6) + (keyword_overlap * 0.4)
        
        return agreement
    
    @staticmethod
    def merge_analyses(
        primary_result: Dict[str, Any],
        secondary_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge results from both AI models into consensus
        """
        # Extract responses
        primary_text = primary_result.get("response", "")
        secondary_text = secondary_result.get("response", "")
        
        primary_success = primary_result.get("success", False)
        secondary_success = secondary_result.get("success", False)
        
        # Handle failures
        if not primary_success and not secondary_success:
            return {
                "consensus_summary": "Both AI models failed to analyze",
                "consensus_confidence": 0.0,
                "agreement_score": 0.0,
                "needs_review": True,
                "primary_summary": "",
                "secondary_summary": "",
                "mode": "failed"
            }
        
        if not primary_success:
            # Only secondary succeeded
            return {
                "consensus_summary": secondary_text,
                "consensus_confidence": 0.7,  # Lower confidence with single model
                "agreement_score": 0.0,
                "needs_review": False,
                "primary_summary": "",
                "secondary_summary": secondary_text,
                "mode": "secondary_only"
            }
        
        if not secondary_success:
            # Only primary succeeded
            return {
                "consensus_summary": primary_text,
                "consensus_confidence": 0.7,  # Lower confidence with single model
                "agreement_score": 0.0,
                "needs_review": False,
                "primary_summary": primary_text,
                "secondary_summary": "",
                "mode": "primary_only"
            }
        
        # Both succeeded - compute consensus
        agreement_score = ConsensusEngine.compute_semantic_agreement(
            primary_text, secondary_text
        )
        
        logger.info(f"Agreement score: {agreement_score:.2f}")
        
        # High agreement - merge insights
        if agreement_score >= CONSENSUS_THRESHOLD:
            # Create merged summary
            consensus = ConsensusEngine._create_merged_summary(
                primary_text, secondary_text, agreement_score
            )
            
            return {
                "consensus_summary": consensus,
                "consensus_confidence": min(0.95, 0.8 + (agreement_score * 0.15)),
                "agreement_score": agreement_score,
                "needs_review": False,
                "primary_summary": primary_text,
                "secondary_summary": secondary_text,
                "mode": "consensus"
            }
        
        # Low agreement - flag for review
        else:
            # Present both perspectives
            consensus = f"""**Technical Analysis (DeepSeek):**
{primary_text}

**Semantic Analysis (Qwen):**
{secondary_text}

**Note:** The two AI models have different interpretations (agreement: {agreement_score:.0%}). Human review recommended."""
            
            return {
                "consensus_summary": consensus,
                "consensus_confidence": 0.5,
                "agreement_score": agreement_score,
                "needs_review": True,
                "primary_summary": primary_text,
                "secondary_summary": secondary_text,
                "mode": "disagreement"
            }
    
    @staticmethod
    def _create_merged_summary(primary: str, secondary: str, agreement: float) -> str:
        """Create a unified summary from both analyses"""
        
        # If very high agreement, just use primary (more technical)
        if agreement > 0.9:
            return primary
        
        # Otherwise, create structured merge
        merged = f"""**Technical Implementation:**
{primary}

**Purpose & Design:**
{secondary}

**Consensus:** Both AI models agree on the core analysis (confidence: {agreement:.0%})"""
        
        return merged
    
    @staticmethod
    def analyze_result_quality(result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the quality of the consensus result
        Returns metrics and recommendations
        """
        mode = result.get("mode", "unknown")
        confidence = result.get("consensus_confidence", 0.0)
        agreement = result.get("agreement_score", 0.0)
        needs_review = result.get("needs_review", False)
        
        quality_metrics = {
            "mode": mode,
            "confidence": confidence,
            "agreement": agreement,
            "needs_review": needs_review,
            "quality_level": "unknown"
        }
        
        # Determine quality level
        if mode == "failed":
            quality_metrics["quality_level"] = "failed"
            quality_metrics["recommendation"] = "AI analysis failed - retry or manual review"
        
        elif mode in ["primary_only", "secondary_only"]:
            quality_metrics["quality_level"] = "moderate"
            quality_metrics["recommendation"] = "Single model analysis - acceptable but less validated"
        
        elif mode == "consensus" and agreement >= HIGH_CONFIDENCE_THRESHOLD:
            quality_metrics["quality_level"] = "excellent"
            quality_metrics["recommendation"] = "High agreement - trust this analysis"
        
        elif mode == "consensus" and agreement >= CONSENSUS_THRESHOLD:
            quality_metrics["quality_level"] = "good"
            quality_metrics["recommendation"] = "Good agreement - reliable analysis"
        
        elif mode == "disagreement":
            quality_metrics["quality_level"] = "uncertain"
            quality_metrics["recommendation"] = "Models disagree - human review recommended"
        
        return quality_metrics


if __name__ == "__main__":
    # Test the consensus engine
    
    # High agreement scenario
    primary = "This function validates user credentials by querying the database and checking password hash. Time complexity is O(1)."
    secondary = "This function handles user authentication by verifying credentials against stored data. Implements secure password validation."
    
    agreement = ConsensusEngine.compute_semantic_agreement(primary, secondary)
    print(f"High agreement test: {agreement:.2%}")
    
    # Low agreement scenario
    primary2 = "This is a sorting algorithm with O(n log n) complexity."
    secondary2 = "This function sends email notifications to users."
    
    agreement2 = ConsensusEngine.compute_semantic_agreement(primary2, secondary2)
    print(f"Low agreement test: {agreement2:.2%}")
    
    # Test merge
    result = ConsensusEngine.merge_analyses(
        {"response": primary, "success": True, "model": "deepseek"},
        {"response": secondary, "success": True, "model": "qwen"}
    )
    
    print(f"\nConsensus result:")
    print(f"Confidence: {result['consensus_confidence']:.2%}")
    print(f"Mode: {result['mode']}")
    print(f"Summary: {result['consensus_summary'][:100]}...")
