"""
Question Classifier - Route questions to appropriate handlers
Uses rule-based + lightweight heuristics (NO LLM to save quota)
"""
from typing import Tuple
from modules.categories import (
    QuestionCategory,
    READING_PATTERNS,
    MATH_KEYWORDS,
    REFUSAL_KEYWORDS,
    HISTORY_KEYWORDS,
    CULTURE_KEYWORDS,
    GEOGRAPHY_KEYWORDS,
    POLITICS_KEYWORDS,
    contains_keywords
)


class QuestionClassifier:
    """Classify questions into categories using rule-based approach"""

    def classify(self, question: str) -> Tuple[QuestionCategory, float]:
        """
        Classify question into a category

        Args:
            question: The question text

        Returns:
            Tuple of (category, confidence_score)
        """
        # Rule 1: Reading comprehension (highest priority)
        if self._is_reading_comprehension(question):
            return QuestionCategory.READING_COMPREHENSION, 1.0

        # Rule 2: Refusal questions (high priority for safety)
        if self._is_refusal(question):
            return QuestionCategory.REFUSAL, 0.95

        # Rule 3: Math/Logic (clear patterns)
        if self._is_math_logic(question):
            return QuestionCategory.MATH_LOGIC, 0.9

        # Rule 4-7: Domain classification (keyword-based)
        domain_scores = {
            QuestionCategory.HISTORY_VIETNAM: self._score_history(question),
            QuestionCategory.CULTURE_VIETNAM: self._score_culture(question),
            QuestionCategory.GEOGRAPHY_VIETNAM: self._score_geography(question),
            QuestionCategory.POLITICS_LAW: self._score_politics(question)
        }

        # Get highest scoring domain
        best_domain = max(domain_scores, key=domain_scores.get)
        best_score = domain_scores[best_domain]

        # If score is high enough, use that category
        if best_score >= 0.3:
            return best_domain, best_score

        # Fallback to general
        return QuestionCategory.GENERAL, 0.5

    def _is_reading_comprehension(self, question: str) -> bool:
        """Check if question has reading comprehension pattern"""
        return any(pattern in question for pattern in READING_PATTERNS)

    def _is_refusal(self, question: str) -> bool:
        """Check if question should be refused"""
        # Count refusal keywords
        refusal_count = sum(1 for kw in REFUSAL_KEYWORDS
                           if kw.lower() in question.lower())

        # Check for suspicious patterns
        suspicious_patterns = [
            "làm cách nào để tránh",
            "cách để trốn",
            "làm sao để không cung cấp",
            "tránh việc",
            "không bị phát hiện"
        ]

        has_suspicious = any(p in question.lower() for p in suspicious_patterns)

        return refusal_count >= 2 or has_suspicious

    def _is_math_logic(self, question: str) -> bool:
        """Check if question is math/logic"""
        # Có số + có keyword math
        has_number = any(c.isdigit() for c in question)
        has_math_keyword = contains_keywords(question, MATH_KEYWORDS)

        # Hoặc có công thức pattern
        has_formula = any(sym in question for sym in ['=', '+', '-', '*', '/', '(', ')'])

        return (has_number and has_math_keyword) or has_formula

    def _score_history(self, question: str) -> float:
        """Score for history category"""
        score = 0.0

        # Check keywords
        keyword_count = sum(1 for kw in HISTORY_KEYWORDS
                           if kw in question.lower())
        score += min(keyword_count * 0.15, 0.6)

        # Boost for year patterns
        if any(str(year) in question for year in range(1000, 2025)):
            score += 0.3

        # Boost for historical names (Nhà X, vua X)
        if "nhà " in question.lower() or "vua " in question.lower():
            score += 0.2

        return min(score, 1.0)

    def _score_culture(self, question: str) -> float:
        """Score for culture category"""
        score = 0.0

        keyword_count = sum(1 for kw in CULTURE_KEYWORDS
                           if kw in question.lower())
        score += min(keyword_count * 0.2, 0.8)

        # Boost for cultural terms
        if any(term in question.lower() for term in ["văn học", "tác phẩm", "lễ hội", "tết"]):
            score += 0.3

        return min(score, 1.0)

    def _score_geography(self, question: str) -> float:
        """Score for geography category"""
        score = 0.0

        keyword_count = sum(1 for kw in GEOGRAPHY_KEYWORDS
                           if kw in question.lower())
        score += min(keyword_count * 0.2, 0.8)

        # Boost for location terms
        if any(term in question.lower() for term in ["tỉnh", "thành phố", "sông", "núi"]):
            score += 0.3

        return min(score, 1.0)

    def _score_politics(self, question: str) -> float:
        """Score for politics/law category"""
        score = 0.0

        keyword_count = sum(1 for kw in POLITICS_KEYWORDS
                           if kw in question.lower())
        score += min(keyword_count * 0.2, 0.8)

        # Boost for political/legal terms
        if any(term in question.lower() for term in ["luật", "hiến pháp", "chính phủ", "quy định"]):
            score += 0.3

        return min(score, 1.0)


# Singleton
classifier = QuestionClassifier()
