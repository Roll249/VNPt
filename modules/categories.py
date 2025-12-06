"""
Question categories and classification
"""
from enum import Enum
from typing import List, Set


class QuestionCategory(Enum):
    """Question categories for specialized handling"""
    READING_COMPREHENSION = "reading"
    MATH_LOGIC = "math"
    REFUSAL = "refusal"
    HISTORY_VIETNAM = "history"
    CULTURE_VIETNAM = "culture"
    GEOGRAPHY_VIETNAM = "geography"
    POLITICS_LAW = "politics"
    GENERAL = "general"  # fallback


# Keywords for rule-based classification
READING_PATTERNS = [
    "Đoạn thông tin:",
    "-- Đoạn văn",
    "[1] Tiêu đề:",
    "Theo đoạn văn",
    "Dựa vào đoạn văn"
]

MATH_KEYWORDS = [
    "tính", "tính toán", "tính được",
    "công thức", "phương trình",
    "xác định", "độ co giãn",
    "điện trở", "tương đương",
    "diện tích", "thể tích",
    "xác suất", "tổ hợp",
    "giải", "đạo hàm", "tích phân"
]

REFUSAL_KEYWORDS = [
    "trốn", "tránh", "lẩn tránh",
    "gian lận", "lừa đảo", "lừa gạt",
    "vi phạm", "trái phép",
    "bất hợp pháp", "phi pháp",
    "tham nhũng", "hối lộ",
    "trốn thuế", "tránh thuế",
    "làm cách nào để tránh",
    "cách để trốn",
    "làm sao để không"
]

HISTORY_KEYWORDS = [
    "nhà", "triều đại", "vua",
    "năm", "thế kỷ",
    "kháng chiến", "chiến tranh",
    "cách mạng", "độc lập",
    "thời kỳ", "giai đoạn",
    "sự kiện", "trận",
    "lịch sử", "xưa"
]

CULTURE_KEYWORDS = [
    "lễ hội", "tết",
    "văn học", "tác phẩm", "tác giả",
    "ca dao", "tục ngữ",
    "nghệ thuật", "hội họa",
    "văn hóa", "truyền thống",
    "phong tục", "tập quán",
    "ẩm thực", "món ăn",
    "di sản"
]

GEOGRAPHY_KEYWORDS = [
    "tỉnh", "thành phố",
    "sông", "núi", "đảo",
    "đồng bằng", "vùng",
    "khí hậu", "thời tiết",
    "dân số", "diện tích",
    "vị trí địa lý",
    "nằm ở", "thuộc"
]

POLITICS_KEYWORDS = [
    "hiến pháp", "luật", "nghị định",
    "quốc hội", "chính phủ",
    "đảng", "chính trị",
    "chủ tịch", "thủ tướng",
    "bộ trưởng",
    "quyền", "nghĩa vụ",
    "pháp luật", "quy định"
]


def contains_keywords(text: str, keywords: List[str]) -> bool:
    """Check if text contains any of the keywords"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)
