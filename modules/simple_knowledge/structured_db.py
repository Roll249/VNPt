"""
Structured facts database by topic
"""

DB_HISTORY = {
    # Dynasties
    "nhà lý": "Nhà Lý (1009-1225): Thành lập bởi Lý Công Uẩn (Lý Thái Tổ), dời đô về Thăng Long (1010), đổi tên nước là Đại Việt (1054).",
    "nhà trần": "Nhà Trần (1225-1400): Nổi bật với hào khí Đông A, 3 lần thắng quân Mông-Nguyên. Các vua: Trần Thái Tông, Trần Thánh Tông, Trần Nhân Tông.",
    "nhà lê": "Nhà Hậu Lê (1428-1789): Lê Lợi thành lập sau khởi nghĩa Lam Sơn. Lê Thánh Tông đưa đất nước phát triển rực rỡ (Luật Hồng Đức).",
    "nhà nguyễn": "Nhà Nguyễn (1802-1945): Triều đại phong kiến cuối cùng. Vua Gia Long đặt tên nước Việt Nam.",

    # Figures
    "lý công uẩn": "Lý Công Uẩn (Lý Thái Tổ): Vua sáng lập nhà Lý, ban Chiếu dời đô.",
    "lý thường kiệt": "Lý Thường Kiệt: Danh tướng nhà Lý, đánh Tống, tác giả 'Nam quốc sơn hà'.",
    "trần hưng đạo": "Trần Hưng Đạo (Trần Quốc Tuấn): Tiết chế thống lĩnh quân đội nhà Trần, viết 'Hịch tướng sĩ'.",
    "nguyễn trãi": "Nguyễn Trãi: Danh nhân văn hóa, quân sư của Lê Lợi, viết 'Bình Ngô đại cáo'.",
    "quang trung": "Quang Trung (Nguyễn Huệ): Thần tốc đánh bại 29 vạn quân Thanh (1789), trận Ngọc Hồi - Đống Đa.",
    "hồ chí minh": "Hồ Chí Minh: Lãnh tụ vĩ đại, đọc Tuyên ngôn Độc lập (2/9/1945), sáng lập Đảng CS Việt Nam.",
    "võ nguyên giáp": "Võ Nguyên Giáp: Đại tướng, Tổng tư lệnh, chỉ huy chiến dịch Điện Biên Phủ (1954).",
    
    # Events
    "điện biên phủ": "Chiến thắng Điện Biên Phủ (7/5/1954): 'Lừng lẫy năm châu, chấn động địa cầu', kết thúc kháng chiến chống Pháp.",
    "cách mạng tháng tám": "Cách mạng Tháng Tám (1945): Giành chính quyền từ tay phát xít Nhật, thành lập nước VNDCCH.",
    "đại thắng mùa xuân": "Đại thắng mùa Xuân 1975: Chiến dịch Hồ Chí Minh giải phóng miền Nam, thống nhất đất nước (30/4/1975).",
}

DB_GEOGRAPHY = {
    # Cities/Provinces
    "hà nội": "Hà Nội: Thủ đô, vị trí trung tâm ĐBSH. Các tên cũ: Thăng Long, Đông Đô, Đông Quan.",
    "hồ chí minh": "TP. Hồ Chí Minh: Thành phố đông dân nhất, trung tâm kinh tế phía Nam. Tên cũ: Sài Gòn, Gia Định.",
    "đà nẵng": "Đà Nẵng: Thành phố đáng sống, cầu Rồng, bãi biển Mỹ Khê.",
    "cần thơ": "Cần Thơ: Trung tâm ĐBSCL, nổi tiếng bến Ninh Kiều, chợ nổi Cái Răng.",
    "huế": "Huế: Cố đô triều Nguyễn, di sản văn hóa thế giới, sông Hương núi Ngự.",

    # Natural
    "sông hồng": "Sông Hồng: Hệ thống sông lớn nhất miền Bắc, bồi đắp ĐBSH. Màu nước đỏ nặng phù sa.",
    "sông cửu long": "Sông Cửu Long (Mê Kông): Chảy vào VN qua 2 nhánh Tiền và Hậu, đổ ra biển bằng 9 cửa.",
    "fansipan": "Fansipan (Phan Xi Păng): Nóc nhà Đông Dương, cao 3.143m, thuộc dãy Hoàng Liên Sơn (Lào Cai).",
    "biển đông": "Biển Đông: Vùng biển chiến lược, chứa hai quần đảo Hoàng Sa (Đà Nẵng) và Trường Sa (Khánh Hòa).",
}

DB_CULTURE = {
    # Literature
    "truyện kiều": "Truyện Kiều (Đoạn trường tân thanh): Kiệt tác truyện thơ Nôm của Nguyễn Du.",
    "nam quốc sơn hà": "Nam quốc sơn hà: Bản tuyên ngôn độc lập đầu tiên, tương truyền của Lý Thường Kiệt.",
    "bình ngô đại cáo": "Bình Ngô đại cáo: Bản tuyên ngôn độc lập thứ hai, của Nguyễn Trãi.",
    
     # Traditions
    "tết nguyên đán": "Tết Nguyên Đán: Tết Âm lịch, lễ hội lớn nhất. Có bánh chưng (Bắc), bánh tét (Nam).",
    "giỗ tổ": "Giỗ Tổ Hùng Vương: 10/3 Âm lịch tại đền Hùng (Phú Thọ). 'Dù ai đi ngược về xuôi...'",
    "nhã nhạc": "Nhã nhạc cung đình Huế: Di sản văn hóa phi vật thể của nhân loại (UNESCO).",
    "cồng chiêng": "Không gian văn hóa Cồng chiêng Tây Nguyên: Di sản văn hóa phi vật thể (UNESCO).",
}

DB_POLITICS_LAW = {
    # Political System
    "đảng cộng sản": "Đảng Cộng sản Việt Nam: Đội tiên phong của giai cấp công nhân, lãnh đạo Nhà nước và xã hội.",
    "quốc hội": "Quốc hội: Cơ quan đại biểu cao nhất của Nhân dân, cơ quan quyền lực Nhà nước cao nhất.",
    "chủ tịch nước": "Chủ tịch nước: Người đứng đầu Nhà nước, thay mặt nước CHXHCNVN về đối nội, đối ngoại.",
    "chính phủ": "Chính phủ: Cơ quan hành chính Nhà nước cao nhất, thực hiện quyền hành pháp. Đứng đầu là Thủ tướng.",
    
    # Law Laws
    "hiến pháp": "Hiến pháp: Đạo luật cơ bản, có hiệu lực pháp lý cao nhất. Bản hiện hành: Hiến pháp 2013.",
    "bộ luật hình sự": "Tuổi chịu trách nhiệm hình sự: Từ đủ 16 tuổi (mọi tội), từ 14-16 (tội rất/đặc biệt nghiêm trọng).",
    "luật hôn nhân": "Tuổi kết hôn: Nam từ đủ 20, Nữ từ đủ 18. Cấm kết hôn trong phạm vi 3 đời.",
    "luật giao thông": "Nồng độ cồn: Cấm tuyệt đối khi lái xe (Nghị định 100). Xe máy dưới 50cc cho người đủ 16 tuổi.",
}

# Combine all
STRUCTURED_DB = {}
STRUCTURED_DB.update(DB_HISTORY)
STRUCTURED_DB.update(DB_GEOGRAPHY)
STRUCTURED_DB.update(DB_CULTURE)
STRUCTURED_DB.update(DB_POLITICS_LAW)
