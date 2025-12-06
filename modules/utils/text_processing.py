"""
Text processing utilities
"""
import re
from typing import Dict, List


def extract_context_from_question(question: str) -> str:
    """
    Extract context from reading comprehension questions

    Args:
        question: Full question text

    Returns:
        Extracted context (the passage to read)
    """
    # Pattern 1: "Đoạn thông tin:\n..."
    if "Đoạn thông tin:" in question:
        parts = question.split("Câu hỏi:")
        if len(parts) >= 2:
            context = parts[0].replace("Đoạn thông tin:", "").strip()
            actual_question = parts[1].strip()
            return context

    # Pattern 2: Multiple paragraphs with "-- Đoạn văn X --"
    if "-- Đoạn văn" in question:
        parts = question.split("Câu hỏi:")
        if len(parts) >= 2:
            context = parts[0].strip()
            return context

    # Default: return first 80% as context if very long
    if len(question) > 1000:
        split_point = int(len(question) * 0.8)
        return question[:split_point]

    return question


def extract_question_from_reading(question: str) -> str:
    """
    Extract just the question part from reading comprehension

    Args:
        question: Full question text

    Returns:
        Just the question
    """
    if "Câu hỏi:" in question:
        parts = question.split("Câu hỏi:")
        if len(parts) >= 2:
            return parts[1].strip()

    return question


def clean_text(text: str) -> str:
    """
    Clean and normalize Vietnamese text

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters (but keep Vietnamese diacritics)
    text = re.sub(r'[^\w\s.,!?;:()\-áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]', '', text, flags=re.IGNORECASE)

    return text.strip()


def contains_math_patterns(text: str) -> bool:
    """Check if text contains mathematical patterns"""
    math_symbols = ['=', '×', '÷', '±', '≤', '≥', '∑', '∫', '√']
    has_symbols = any(sym in text for sym in math_symbols)

    # Check for fractions, equations
    has_fraction = bool(re.search(r'\d+/\d+', text))
    has_equation = bool(re.search(r'[a-zA-Z]\s*=\s*\d', text))

    # Check for numbers with operations
    has_calculation = bool(re.search(r'\d+\s*[\+\-\*/]\s*\d+', text))

    return has_symbols or has_fraction or has_equation or has_calculation


def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    # Match integers and decimals
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)

    numbers = []
    for match in matches:
        try:
            num = float(match)
            numbers.append(num)
        except ValueError:
            continue

    return numbers


def normalize_answer(answer: str) -> str:
    """
    Normalize answer to standard format (A/B/C/D)

    Args:
        answer: Answer text

    Returns:
        Normalized answer (A, B, C, D, etc.)
    """
    answer = answer.strip().upper()

    # Extract first letter if it's A-J
    for char in answer:
        if char in 'ABCDEFGHIJ':
            return char

    # Try to find "Đáp án: X" pattern
    match = re.search(r'[ABCDEFGHIJ]', answer)
    if match:
        return match.group(0)

    # Default
    return 'A'
