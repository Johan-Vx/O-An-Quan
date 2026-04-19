# Project Title

Chuyển đổi đồ án Ô Ăn Quan Desktop sang Web Server

## Demo

- [Ô Ăn Quan Web Server](https://o-an-quan-fmpx.onrender.com/)

# **🎮 Hướng dẫn Cài đặt & Sử dụng Ô Ăn Quan Web**

## **1\. Yêu cầu Hệ thống**

- **Python:** Phiên bản 3.9 trở lên.
- **Trình duyệt:** Chrome, Edge, Safari hoặc Firefox (phiên bản mới nhất).

## **2\. Cấu trúc Thư mục Dự án**

o-an-quan-web/  
├── server/ \# Chứa logic Backend (Python/Flask)  
│ ├── app.py \# Điểm khởi chạy ứng dụng & SocketIO  
│ ├── game_engine.py \# Logic rải quân, ăn quân và xử lý luật  
│ ├── ai.py \# Trí tuệ nhân tạo (Minimax \+ Alpha-Beta)  
│ └── constants.py \# Các hằng số tọa độ và cấu hình game  
├── static/ \# Tài nguyên Frontend (JS, CSS, Images)  
│ ├── js/index.js \# Xử lý Canvas và giao tiếp Real-time  
│ ├── css/ \# Style giao diện  
│ └── images/ \# Ảnh nền bàn cờ (P1/P2) và các quân cờ  
├── templates/ \# Chứa file giao diện HTML  
├── requirements.txt \# Danh sách các thư viện cần cài đặt
├── local.txt \# Danh sách các thư viện cần cài đặt
└── Procfile \# Cấu hình khởi chạy cho Server (Render/Heroku)

## **3\. Cài đặt và Chạy trên Local (Máy cá nhân)**

### **Bước 1: Tải mã nguồn và Cài đặt thư viện**

Mở Terminal hoặc Command Prompt và thực hiện:

\# Di chuyển vào thư mục dự án  
cd o-an-quan-web

\# (Khuyến nghị) Tạo môi trường ảo  
python \-m venv venv  
source venv/bin/activate \# Trên Windows dùng: venv\\Scripts\\activate

\# Cài đặt các thư viện cần thiết  
pip install \-r local.txt

### **Bước 2: Khởi chạy Ứng dụng**

python server/app.py

Sau khi chạy, truy cập địa chỉ: http://localhost:5000 trên trình duyệt.

## **4\. Triển khai lên Server (Render.com)**

Để ứng dụng có thể chơi online với bạn bè, chúng ta sẽ sử dụng Render.com.

### **Bước 1: Chuẩn bị**

1. Đưa toàn bộ mã nguồn lên một **GitHub Repository** công khai hoặc riêng tư.
2. Đăng nhập vào [Render.com](https://render.com).

### **Bước 2: Cấu hình Web Service**

1. Chọn **New \+** \-\> **Web Service**.
2. Kết nối với Repo GitHub
3. Thiết lập các thông số sau:
   - **Runtime:** Python 3
   - **Build Command:** pip install \-r requirements.txt
   - **Start Command:** gunicorn \--worker-class eventlet \-w 1 server.app:app

### **⚠️ Lưu ý Quan trọng về Hiệu suất:**

- **Tham số \-w 1:** Đối với các ứng dụng sử dụng WebSocket (SocketIO), bạn **BẮT BUỘC** phải sử dụng duy nhất 1 worker. Nếu sử dụng nhiều worker, kết nối của người chơi sẽ bị phân tán và không thể thấy nhau trong cùng một phòng.
- **Biến môi trường:** Thêm PYTHON_VERSION với giá trị 3.9.0 trong phần **Environment**

## **5\. Hướng dẫn Sử dụng Ứng dụng (Cách chơi)**

### **A. Chế độ Chơi với Người (PvP \- Online)**

1. **Tạo phòng:** Người chơi 1 nhập tên phòng và nhấn "Tạo". Một mã phòng (Room ID) sẽ xuất hiện.
2. **Tham gia:** Người chơi 2 nhập mã phòng đó và nhấn "Tham gia".
3. **Góc nhìn (Flip View):** \- Player 1 nhìn bàn cờ theo hướng thuận (ô của mình ở dưới).
   - Player 2 sẽ tự động được hệ thống lật ngược bàn cờ để các ô của mình cũng nằm ở hàng dưới, giúp thao tác Trái/Phải không bị ngược.

### **B. Chế độ Chơi với Máy (PvE)**

1. Chọn mức độ khó: **Dễ (Easy)**, **Trung bình (Medium)**, hoặc **Khó (Hard)**.
2. AI sử dụng thuật toán **Minimax** để tính toán. Ở mức Khó, AI có thể nhìn trước 5 nước đi và có chiến thuật bảo vệ Quan rất chặt chẽ.
