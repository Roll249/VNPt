"""
Legal Knowledge Base for Vietnamese Laws
Embedded directly in Python to avoid .gitignore blocking JSON files
"""

LEGAL_KNOWLEDGE = [
    {
        "title": "Hiến pháp Việt Nam 2013",
        "content": """Điều 1: Nước Cộng hòa xã hội chủ nghĩa Việt Nam là một nước độc lập, có chủ quyền, thống nhất và toàn vẹn lãnh thổ, bao gồm đất liền, hải đảo, vùng biển và vùng trời.
Điều 2: Nhà nước Cộng hòa xã hội chủ nghĩa Việt Nam là nhà nước pháp quyền xã hội chủ nghĩa của Nhân dân, do Nhân dân, vì Nhân dân.
Điều 3: Nhà nước bảo đảm và phát huy quyền làm chủ của Nhân dân; công nhận, tôn trọng, bảo vệ và bảo đảm quyền con người, quyền công dân.
Điều 4: Đảng Cộng sản Việt Nam là đội tiên phong của giai cấp công nhân, đồng thời là đội tiên phong của Nhân dân lao động và của dân tộc Việt Nam.""",
        "keywords": ["hiến pháp", "nhà nước", "chủ quyền", "đảng cộng sản"]
    },
    {
        "title": "Luật Giao thông đường bộ 2008",
        "content": """Điều 8: Các hành vi bị nghiêm cấm gồm: Điều khiển xe ô tô, máy kéo, xe máy chuyên dùng trên đường mà trong máu hoặc hơi thở có nồng độ cồn.
Điều 30: Người điều khiển xe mô tô hai bánh, xe gắn máy chỉ được chở một người, trừ trường hợp chở người bệnh đi cấp cứu.
Điều 31: Người đủ 16 tuổi trở lên được điều khiển xe gắn máy có dung tích xi-lanh dưới 50 cm3. Người đủ 18 tuổi trở lên được điều khiển xe mô tô có dung tích xi-lanh từ 50 cm3 trở lên.""",
        "keywords": ["giao thông", "đường bộ", "nồng độ cồn", "xe máy", "tuổi lái xe"]
    },
    {
        "title": "Bộ luật Hình sự 2015",
        "content": """Điều 12: Người từ đủ 16 tuổi trở lên phải chịu trách nhiệm hình sự về mọi tội phạm. Người từ đủ 14 tuổi đến dưới 16 tuổi phải chịu trách nhiệm hình sự về tội phạm rất nghiêm trọng, tội phạm đặc biệt nghiêm trọng.
Điều 134: Tội cố ý gây thương tích.
Điều 168: Tội cướp tài sản.
Điều 173: Tội trộm cắp tài sản.
Điều 260: Tội vi phạm quy định về tham gia giao thông đường bộ.""",
        "keywords": ["hình sự", "tội phạm", "trách nhiệm", "trộm cắp", "cướp", "tuổi chịu trách nhiệm"]
    },
    {
        "title": "Luật Đất đai 2024",
        "content": """Điều 4: Đất đai thuộc sở hữu toàn dân do Nhà nước đại diện chủ sở hữu và thống nhất quản lý.
Điều 5: Nhà nước giao đất, cho thuê đất, công nhận quyền sử dụng đất cho người sử dụng đất.
Điều 6: Người sử dụng đất có quyền chuyển đổi, chuyển nhượng, cho thuê, cho thuê lại, thừa kế, tặng cho quyền sử dụng đất; thế chấp, góp vốn bằng quyền sử dụng đất.""",
        "keywords": ["đất đai", "quyền sử dụng đất", "chuyển nhượng", "thế chấp"]
    },
    {
        "title": "Luật Hôn nhân và Gia đình 2014",
        "content": """Điều 8: Điều kiện kết hôn: Nam từ đủ 20 tuổi trở lên, nữ từ đủ 18 tuổi trở lên. Việc kết hôn do nam và nữ tự nguyện quyết định. Không thuộc trường hợp cấm kết hôn.
Điều 9: Cấm kết hôn trong các trường hợp: Kết hôn giả tạo, lừa dối; Người đang có vợ, có chồng mà kết hôn với người khác; Giữa những người cùng dòng máu về trực hệ; giữa những người có họ trong phạm vi ba đời.""",
        "keywords": ["hôn nhân", "gia đình", "kết hôn", "tuổi kết hôn", "cấm kết hôn"]
    },
    {
        "title": "Luật Lao động 2019",
        "content": """Điều 105: Thời giờ làm việc bình thường không quá 08 giờ trong 01 ngày và không quá 48 giờ trong 01 tuần.
Điều 113: Người lao động làm việc đủ 12 tháng cho một người sử dụng lao động thì được nghỉ hằng năm 12 ngày làm việc, hưởng nguyên lương.
Điều 112: Người lao động được nghỉ làm việc, hưởng nguyên lương trong những ngày lễ, tết: Tết Dương lịch 01 ngày; Tết Âm lịch 05 ngày; Ngày Chiến thắng 01 ngày; Ngày Quốc khánh 02 ngày.""",
        "keywords": ["lao động", "nghỉ phép", "ngày lễ", "thời giờ làm việc"]
    },
    {
        "title": "Nghị định 100/2019 về xử phạt vi phạm hành chính giao thông đường bộ",
        "content": """Điều 5: Phạt tiền từ 6.000.000 đến 8.000.000 đồng đối với người điều khiển xe ô tô có nồng độ cồn vượt quá 50 miligam đến 80 miligam/100 mililít máu hoặc vượt quá 0,25 miligam đến 0,4 miligam/1 lít khí thở.
Phạt tiền từ 30.000.000 đến 40.000.000 đồng đối với người điều khiển xe ô tô có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở.""",
        "keywords": ["nghị định 100", "phạt", "nồng độ cồn", "vi phạm giao thông"]
    },
    {
        "title": "Luật Doanh nghiệp 2020",
        "content": """Điều 4: Doanh nghiệp là tổ chức có tên riêng, có tài sản, có trụ sở giao dịch, được thành lập hoặc đăng ký thành lập theo quy định của pháp luật nhằm mục đích kinh doanh.
Điều 74: Công ty trách nhiệm hữu hạn một thành viên là doanh nghiệp do một tổ chức hoặc một cá nhân làm chủ sở hữu.
Điều 111: Công ty cổ phần là doanh nghiệp có vốn điều lệ được chia thành nhiều phần bằng nhau gọi là cổ phần.""",
        "keywords": ["doanh nghiệp", "công ty cổ phần", "công ty tnhh", "kinh doanh"]
    }
]


def search_legal(query: str, top_k: int = 3) -> list:
    """Search legal knowledge base by keyword matching"""
    query_lower = query.lower()
    results = []
    
    for doc in LEGAL_KNOWLEDGE:
        score = 0
        # Check title
        if any(word in doc["title"].lower() for word in query_lower.split()):
            score += 2
        # Check keywords
        for kw in doc["keywords"]:
            if kw in query_lower:
                score += 3
        # Check content
        if any(word in doc["content"].lower() for word in query_lower.split() if len(word) > 2):
            score += 1
        
        if score > 0:
            results.append((score, doc))
    
    results.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in results[:top_k]]
