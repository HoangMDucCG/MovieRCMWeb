Dự án này được xây dựng bằng Python và Django Framework. Làm theo các bước dưới đây để cài đặt và chạy dự án trên máy tính:

Yêu cầu cơ bản (Prerequisites):
Đã cài đặt Python (phiên bản 3.8 trở lên).
Đã cài đặt Git.

Bước 1: Clone dự án về máy
Mở Command Prompt và chạy lệnh sau:
git clone https://github.com/HoangMDucCG/MovieRCMWeb.git
cd MovieRCMWebDB

Bước 2: Tạo và kích hoạt môi trường ảo (Virtual Environment)
- Trên Windows:
python -m venv venv
venv\Scripts\activate
- Trên MacOS/Linux:
python3 -m venv venv
source venv/bin/activate

Bước 3: Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

Bước 4: Cấu hình API Key cho Chatbot Gemini
Dự án sử dụng Google Gemini AI để làm trợ lý tư vấn phim. Bạn cần có API Key để chatbot hoạt động:
Lấy API Key miễn phí tại Google AI Studio.
Tạo file .env cùng cấp với manage.py
Tạo API_KEY = "..." và thay thế bằng API Key của bạn.

Bước 5: Khởi tạo Cơ sở dữ liệu (Database)
**Mặc định Django sẽ dùng SQLite. Tuy nhiên, kiến trúc dự án được thiết kế linh hoạt để kết nối với các RDBMS lớn. Nếu bạn định cấu hình web kết nối với SQL Server hoặc MySQL thông qua DBeaver/SSMS, bạn cần cài thêm driver tương ứng.

Tạo cơ sở dữ liệu trống cục bộ và lưu thông tin Database vào core/settings.py và tiến hành chạy lệnh:
python manage.py makemigrations
python manage.py migrate

Bước 6: Kiểm tra hệ thống
Chạy lệnh: python manage.py test
Nếu hệ thống báo OK tức là mọi chức năng của hệ thống đã hoạt động.
Nếu báo fail kiểm tra fail tại test nào và tiến hành chỉnh sửa, bổ sung.

Bước 7: Tạo tài khoản Quản trị viên (Admin)
Tạo một tài khoản admin:
python manage.py createsuperuser

Bước 8: Chạy server
Khởi động máy chủ phát triển (Development Server) cục bộ:
python manage.py runserver

Bây giờ, bạn có thể mở trình duyệt và truy cập vào:
Trang web chính: http://127.0.0.1:8000/
Trang quản trị (để thêm dữ liệu phim): http://127.0.0.1:8000/admin/

**Lưu ý:
Vì database hoàn toàn trống, trang web ban đầu sẽ chưa có phim nào hiển thị. Bạn hãy đăng nhập vào đường dẫn http://127.0.0.1:8000/admin/ bằng tài khoản Superuser vừa tạo ở Bước 7 để thêm Thể loại (Genres), Phim (Movies) và Link rạp/Online (TheaterLinks). Chatbot AI cũng sẽ tự động học và tư vấn dựa trên dữ liệu bạn vừa thêm vào!