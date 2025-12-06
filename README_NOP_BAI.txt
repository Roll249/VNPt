================================================================
        HƯỚNG DẪN NỘP BÀI - VNPT AI HACKATHON TRACK 2
================================================================

📦 NỘI DUNG NỘP: DOCKER IMAGE
⏱️  Thời gian build: ~5-10 phút
💾 Kích thước: ~2.6GB
✅ Accuracy: 60% (tested)

================================================================
BƯỚC 1: MỞ COMMAND PROMPT
================================================================

Windows Key + R → nhập "cmd" → Enter

Hoặc: PowerShell (Windows Key + X → chọn PowerShell)

================================================================
BƯỚC 2: DI CHUYỂN ĐẾN THƯ MỤC DỰ ÁN
================================================================

cd D:\Khang\Thi\VNPT

================================================================
BƯỚC 3: BUILD DOCKER IMAGE
================================================================

docker build -t vnpt-qa-system .

⏳ Đợi ~5-10 phút để build xong
✅ Khi thấy "Successfully built" là xong

================================================================
BƯỚC 4: TEST LOCAL (TÙY CHỌN - ĐỂ KIỂM TRA)
================================================================

A. Tạo thư mục test:
   mkdir test_data
   mkdir test_output

B. Copy file test:
   copy data\val_10.json test_data\private_test.json

C. Chạy Docker:
   docker run --rm -v "%cd%\test_data:/code/data" -v "%cd%\test_output:/code/output" vnpt-qa-system

D. Xem kết quả:
   type test_output\submission.csv

   Phải có format:
   qid,answer
   val_0001,B
   val_0002,C
   ...

================================================================
BƯỚC 5: NỘP BÀI
================================================================

🔹 CÁCH 1 - Docker Hub (KHUYẾN NGHỊ):

1. Đăng nhập Docker Hub:
   docker login
   Username: [nhập username]
   Password: [nhập password]

2. Tag image:
   docker tag vnpt-qa-system [YOUR_USERNAME]/vnpt-qa-system:latest

   Ví dụ:
   docker tag vnpt-qa-system nguyenvana/vnpt-qa-system:latest

3. Push lên Docker Hub:
   docker push [YOUR_USERNAME]/vnpt-qa-system:latest

4. NỘP LINK NÀY:
   [YOUR_USERNAME]/vnpt-qa-system:latest

----------------------------------------------------------------

🔹 CÁCH 2 - Save File .tar:

1. Save Docker image ra file:
   docker save vnpt-qa-system > vnpt-qa-system.tar

2. Nén file (optional):
   # Dùng 7-Zip hoặc WinRAR để nén
   # Hoặc PowerShell:
   Compress-Archive -Path vnpt-qa-system.tar -DestinationPath vnpt-qa-system.zip

3. NỘP FILE:
   vnpt-qa-system.tar (~2.6GB)
   hoặc vnpt-qa-system.zip (~1.5GB nếu nén)

================================================================
THÔNG TIN HỆ THỐNG
================================================================

✅ Base Image: nvidia/cuda:12.2.0-runtime-ubuntu20.04
✅ Python: 3.9
✅ Dependencies: requests, numpy, pandas, faiss-cpu (46MB)
✅ Size: 2.6GB
✅ Accuracy: 60% (6/10 trên validation test)
✅ Speed: ~8-10 phút cho 400 câu hỏi
✅ Memory: ~500MB

================================================================
CẤU TRÚC SOURCE CODE BÊN TRONG
================================================================

/code/
├── predict.py              (Main file - entry point)
├── api-keys.json          (VNPT API credentials)
├── requirements.txt       (Dependencies)
├── config/
│   └── api_config.py
└── modules/
    ├── categories.py
    ├── question_classifier.py
    ├── simple_knowledge.py
    ├── llm/api_client.py
    └── utils/text_processing.py

================================================================
DOCKER INPUT/OUTPUT SPECIFICATION
================================================================

📥 INPUT:
   Path: /code/data/private_test.json
   Format: JSON array với qid, question, choices

📤 OUTPUT:
   Path: /code/output/submission.csv
   Format: CSV với header "qid,answer"

================================================================
TROUBLESHOOTING
================================================================

❌ "docker: command not found"
   → Cài Docker Desktop: https://www.docker.com/products/docker-desktop

❌ "Cannot connect to Docker daemon"
   → Mở Docker Desktop trước khi chạy lệnh

❌ Build lỗi "no space left"
   → Dọn dẹp Docker: docker system prune -a

❌ "Failed to push image"
   → Kiểm tra docker login và username

================================================================
LIÊN HỆ & HỖ TRỢ
================================================================

Nếu gặp vấn đề, kiểm tra:
1. Docker Desktop đã chạy chưa
2. Internet connection (cần tải base image)
3. Đủ dung lượng ổ đĩa (~10GB free)

================================================================
CHECK LIST TRƯỚC KHI NỘP
================================================================

□ Docker image đã build thành công
□ Đã test local và có file submission.csv
□ File CSV đúng format (header + rows)
□ Đã push lên Docker Hub hoặc save file .tar
□ Có link/file để nộp

================================================================

✅ SẴN SÀNG NỘP!

Theo hướng dẫn của ban tổ chức để submit:
- Link Docker Hub: [YOUR_USERNAME]/vnpt-qa-system:latest
- Hoặc file: vnpt-qa-system.tar

================================================================
Last updated: 06/12/2025
Deadline: 19/12/2025
================================================================
