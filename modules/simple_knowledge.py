"""
Simple knowledge cache for common Vietnamese facts
Lightweight alternative to full RAG - just hardcoded facts
"""

# Common knowledge - key: keyword to match, value: fact
SIMPLE_FACTS = {
    # History
    "nhà lý": "Nhà Lý được thành lập năm 1009 bởi Lý Công Uẩn",
    "lý công uẩn": "Lý Công Uẩn thành lập nhà Lý năm 1009, đóng đô ở Thăng Long (Hà Nội)",
    "trần hưng đạo": "Trần Hưng Đạo là danh tướng triều Trần, đánh thắng quân Nguyên-Mông 3 lần",
    "điện biên phủ": "Chiến thắng Điện Biên Phủ năm 1954",
    "cách mạng tháng tám": "Cách mạng Tháng Tám thành công năm 1945",
    "nguyễn huệ": "Nguyễn Huệ (Quang Trung) đánh thắng quân Thanh năm 1789",

    # Culture
    "truyện kiều": "Truyện Kiều do Nguyễn Du sáng tác",
    "nguyễn du": "Nguyễn Du là tác giả Truyện Kiều",
    "hồ xuân hương": "Hồ Xuân Hương là nữ thi sĩ nổi tiếng thời phong kiến",
    "áo dài": "Áo dài là trang phục truyền thống của Việt Nam",
    "tết nguyên đán": "Tết Nguyên Đán là lễ hội quan trọng nhất của người Việt",

    # Geography
    "hà nội": "Hà Nội là thủ đô của Việt Nam",
    "thành phố hồ chí minh": "Thành phố Hồ Chí Minh (Sài Gòn) là thành phố lớn nhất Việt Nam",
    "sông hồng": "Sông Hồng chảy qua Hà Nội",
    "sông cửu long": "Sông Cửu Long (sông Mê Kông) ở Nam Bộ",
    "vịnh hạ long": "Vịnh Hạ Long thuộc tỉnh Quảng Ninh",
    "phú quốc": "Phú Quốc là đảo lớn nhất của Việt Nam, thuộc Kiên Giang",

    # Politics/Law
    "hiến pháp": "Hiến pháp hiện hành của Việt Nam được thông qua năm 2013",
    "quốc hội": "Quốc hội là cơ quan quyền lực nhà nước cao nhất",
    "chủ tịch nước": "Chủ tịch nước là người đứng đầu nhà nước",
}


def get_relevant_facts(question: str, max_facts: int = 3) -> list:
    """
    Get relevant facts for a question

    Args:
        question: Question text
        max_facts: Maximum number of facts to return

    Returns:
        List of relevant facts
    """
    question_lower = question.lower()

    relevant = []
    for keyword, fact in SIMPLE_FACTS.items():
        if keyword in question_lower:
            relevant.append(fact)
            if len(relevant) >= max_facts:
                break

    return relevant


def augment_prompt_with_facts(question: str, base_prompt: str) -> str:
    """
    Augment prompt with relevant facts

    Args:
        question: Question text
        base_prompt: Base prompt to augment

    Returns:
        Augmented prompt
    """
    facts = get_relevant_facts(question)

    if not facts:
        return base_prompt

    facts_text = "\n".join([f"- {fact}" for fact in facts])

    augmented = f"""Thông tin tham khảo có thể hữu ích:
{facts_text}

{base_prompt}"""

    return augmented
