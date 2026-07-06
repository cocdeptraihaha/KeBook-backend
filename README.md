# Báo cáo Nghiên cứu & Thiết kế Kiến trúc Hệ thống KeBook: Phân hệ Backend API
## Tiểu luận chuyên ngành Phát triển Hệ thống Web nâng cao

---

## TÓM TẮT ĐỀ TÀI

Hệ thống **KeBook Backend** được phát triển nhằm mục đích cung cấp một nền tảng API hiệu năng cao, bảo mật và khả năng mở rộng tốt cho ứng dụng thương mại điện tử chuyên ngành sách. Hệ thống được xây dựng trên nền tảng **FastAPI**, kết hợp với mô hình lập trình bất đồng bộ (**Asynchronous Programming**) sử dụng **SQLAlchemy 2.0 (Async)** và driver **aiomysql** nhằm tối ưu hóa việc sử dụng tài nguyên tài nguyên phần cứng và tăng khả năng xử lý đồng thời (concurrency).

Báo cáo kỹ thuật này đi sâu vào việc phân tích kiến trúc phân tầng (Layered Architecture), cơ chế xác thực đa nhân tố bao gồm mã khóa một lần (**OTP Email**) và mã hóa mã định danh (**JWT Auth**), phân hệ quản lý kho ảnh đa phương tiện, tích hợp công cụ tính điểm thành viên và công cụ khuyến mãi nâng cao. Toàn bộ thiết kế hệ thống đều tuân thủ các quy chuẩn học thuật và thực tiễn phát triển phần mềm chuyên nghiệp.

---

## 1. GIỚI THIỆU TỔNG QUAN

### 1.1 Đặt vấn đề
Trong kỷ nguyên số, các hệ thống thương mại điện tử đòi hỏi sự phản hồi nhanh chóng, tính nhất quán về dữ liệu và độ an toàn thông tin cao. Các mô hình backend truyền thống đồng bộ (Synchronous) thường gặp nghẽn cổ chai (bottleneck) tại các truy vụ I/O đặc biệt là kết nối cơ sở dữ liệu. Để giải quyết bài toán này, đề tài nghiên cứu ứng dụng mô hình bất đồng bộ (Asynchronous) thông qua Framework FastAPI nhằm xây dựng một API trung tâm đáp ứng toàn bộ các yêu cầu nghiệp vụ phức tạp của nền tảng KeBook.

### 1.2 Phạm vi dự án
Phân hệ **KeBook Backend** đóng vai trò là lõi xử lý trung tâm (Core API Engine), phục vụ toàn bộ các luồng dữ liệu cho Frontend thông qua giao thức RESTful API. Hệ thống độc lập hoàn toàn với lớp trình diễn (Presentation Layer) và sẵn sàng tích hợp với đa dạng các nền tảng Client (Web, Mobile, Third-party).

---

## 2. KIẾN TRÚC HỆ THỐNG & MÔ HÌNH THIẾT KẾ

### 2.1 Mô hình Phân tầng (Layered Architecture Pattern)
Hệ thống được tổ chức chặt chẽ theo 4 lớp độc lập nhằm tách biệt mối quan tâm (Separation of Concerns) và tăng khả năng bảo trì, kiểm thử:

```
[ Client: Web / App / Postman ]
               │  ▲
               ▼  │  (HTTP Requests / JSON Responses)
┌────────────────────────────────────────────────────────┐
│ 1. API Route Layer (app/api/)                          │
│    - Tiếp nhận request, phân tích và kiểm chuẩn schema │
│    - Phân quyền truy cập thông qua dependencies        │
└──────────────────────────┬─────────────────────────────┘
                           │  ▲
                           ▼  │
┌────────────────────────────────────────────────────────┐
│ 2. Business Service Layer (app/services/)              │
│    - Chứa đựng logic nghiệp vụ của hệ thống            │
│    - Điều phối các giao dịch phức tạp                  │
└──────────────────────────┬─────────────────────────────┘
                           │  ▲
                           ▼  │
┌────────────────────────────────────────────────────────┐
│ 3. Data Repository Layer (app/repositories/)           │
│    - Trừu tượng hóa việc truy vấn cơ sở dữ liệu        │
│    - Sử dụng mô hình mẫu Repository Pattern            │
└──────────────────────────┬─────────────────────────────┘
                           │  ▲
                           ▼  │
┌────────────────────────────────────────────────────────┐
│ 4. Data Access Layer (app/models/ & app/schemas/)      │
│    - Models: Định nghĩa các thực thể ánh xạ SQL        │
│    - Schemas: Định nghĩa lớp kiểm chuẩn Pydantic       │
└────────────────────────────────────────────────────────┘
```

- **API Layer (`app/api/`):** Chịu trách nhiệm định tuyến (routing), parse dữ liệu đầu vào và chuyển đổi đầu ra thông qua Pydantic Schemas. Đồng thời, đây là nơi áp dụng các Dependency Injection cho việc xác thực và phân quyền người dùng.
- **Service Layer (`app/services/`):** Đảm nhiệm xử lý logic nghiệp vụ chính. Toàn bộ tính toán phức tạp như tính điểm loyalty, xác thực OTP, áp dụng mã giảm giá và điều phối trạng thái đơn hàng đều được đóng gói tại đây.
- **Repository Layer (`app/repositories/`):** Lớp trung gian thực hiện việc giao tiếp trực tiếp với cơ sở dữ liệu thông qua SQLAlchemy AsyncSession. Việc áp dụng Repository Pattern giúp cô lập hoàn toàn câu lệnh SQL/ORM khỏi logic nghiệp vụ, giúp dễ dàng thay đổi hệ quản trị cơ sở dữ liệu nếu cần.
- **Model & Schema Layer (`app/models/` & `app/schemas/`):** 
  - `models/` đại diện cho các thực thể vật lý trong cơ sở dữ liệu (Database Entities).
  - `schemas/` định nghĩa cấu trúc dữ liệu truyền tải qua mạng (Data Transfer Objects - DTO) thông qua Pydantic v2 để tự động hóa quá trình xác thực dữ liệu đầu vào và đầu ra.

### 2.2 Giải pháp Xử lý Bất đồng bộ (Asynchronous Programming)
Khác với các framework đồng bộ truyền thống như Flask hay Django (phiên bản cũ), KeBook Backend tận dụng tối đa cơ chế `async/await` của Python và thư viện `asyncio`.
- **Lợi ích:** Giải phóng luồng xử lý (thread) khi gặp các tác vụ I/O-bound (gửi mail, truy vấn DB, gọi API bên thứ ba như Cloudinary), cho phép một Worker duy nhất có thể tiếp nhận và xử lý hàng ngàn kết nối đồng thời.
- **Quản lý kết nối cơ sở dữ liệu (Connection Pooling):** Thiết lập thông qua `create_async_engine` của SQLAlchemy kết hợp với thư viện Driver `aiomysql`. Cấu hình cơ chế tái sử dụng kết nối (pool size, max overflow) giúp giảm thiểu tối đa độ trễ từ việc thiết lập bắt tay TCP/IP liên tục với database server MySQL.

---

## 3. THIẾT KẾ CƠ SỞ DỮ LIỆU & THỰC THỂ (DATABASE DESIGN)

Cơ sở dữ liệu của KeBook được thiết kế chuẩn hóa cao (3NF) để tránh dư thừa và đảm bảo tính toàn vẹn dữ liệu. Các thực thể chính bao gồm:

1. **User & Authentication:**
   - `users`: Lưu trữ thông tin định danh khách hàng, mật khẩu đã mã hóa (bcrypt), vai trò (admin/user), trạng thái hoạt động (`is_active`), và số điểm tích lũy (`loyalty_points`).
   - `otps`: Lưu trữ mã OTP ngẫu nhiên kèm thời gian hết hạn (`expires_at`) phục vụ xác thực đăng ký tài khoản và khôi phục mật khẩu.

2. **Catalog & Media:**
   - `books`: Chứa thông tin chi tiết về sách, số lượng tồn kho, giá bán, tác giả, mô tả.
   - `categories`: Danh mục phân loại sách theo mô hình quan hệ phân cấp.
   - `book_images`: Thực thể liên kết hỗ trợ thiết lập quan hệ một-nhiều (One-to-Many) giữa một cuốn sách và nhiều hình ảnh chi tiết khác nhau.

3. **Cart & Transactions:**
   - `cart_items`: Quản lý giỏ hàng trực tuyến tạm thời của người dùng.
   - `orders`: Lưu trữ thông tin đơn hàng, thông tin giao hàng chi tiết, trạng thái thanh toán và tổng giá trị đơn hàng.
   - `order_items`: Lưu trữ chi tiết từng sản phẩm trong đơn hàng kèm giá tại thời điểm mua.

4. **Loyalty, Promotions & Support:**
   - `promotions` & `user_promotions`: Quản lý mã giảm giá hệ thống và các mã giảm giá cá nhân của từng khách hàng.
   - `point_rewards`: Định nghĩa các phần quà mà khách hàng có thể dùng điểm thành viên để quy đổi.
   - `support_requests`: Tiếp nhận các yêu cầu trợ giúp và phản hồi từ khách hàng.
   - `notifications`: Hệ thống thông báo thời gian thực và lịch sử thông báo của người dùng.

---

## 4. CHI TIẾT CÁC PHÂN HỆ NGHIỆP VỤ CHÍNH

### 4.1 Quy trình Xác thực Bảo mật Đa nhân tố (Auth Flow)
Hệ thống triển khai quy trình đăng ký nghiêm ngặt nhằm tránh tài khoản rác (spam accounts):

```
[ Đăng ký: POST /auth/register ] ──► [ Tạo User (is_active=0) ] ──► [ Gửi OTP qua Email ]
                                                                             │
[ Login thất bại (chưa active) ] ◄── [ Verify OTP: POST /verify-otp ] ◄──────┘
                                             │
                                             ▼
                                 [ Kích hoạt User (is_active=1) ]
                                             │
                                             ▼
                                 [ Đăng nhập: POST /auth/login ] ──► [ Trả về JWT Access Token ]
```

- **Mật khẩu:** Được băm an toàn bằng thuật toán **Bcrypt** với độ phức tạp cao trước khi lưu vào cơ sở dữ liệu.
- **OTP Engine (`otp_service.py`):** Tạo ra mã số ngẫu nhiên có cấu hình độ dài linh hoạt, giới hạn thời gian tồn tại trong 5 phút.
- **JWT Authentication:** Sau khi đăng nhập thành công bằng email/password, hệ thống cấp phát một Token dạng **JWT (JSON Web Token)** được ký bằng thuật toán đối xứng HMAC-SHA256 với mã hóa khóa bí mật (`SECRET_KEY`). Lớp API Gateway sẽ giải mã và kiểm tra hạn sử dụng của token này trong mỗi request cần định danh thông qua cơ chế Dependency Injection.

### 4.2 Công cụ Khuyến mãi & Điểm Thành viên (Loyalty & Promotion Engine)
- **Hệ thống Điểm tích lũy (`points_service.py`):** Khi người dùng mua hàng thành công, hệ thống tự động cộng điểm tích lũy theo tỷ lệ phần trăm giá trị hóa đơn. Điểm này có thể được dùng để đổi các Voucher giảm giá hoặc các phần quà vật lý thông qua cơ chế trừ điểm giao dịch có khóa an toàn (Transactional locking).
- **Áp dụng khuyến mãi (`promotion_service.py`):** Hỗ trợ kiểm chuẩn đồng thời nhiều ràng buộc: hạn sử dụng, số lượng mã còn lại trong hệ thống, giá trị đơn hàng tối thiểu, sự tương thích giữa các nhóm khuyến mãi và đảm bảo mỗi mã giảm giá chỉ được dùng số lần giới hạn trên mỗi user.

### 4.3 Tác vụ dọn dẹp nền (Background Tasks & Garbage Collection)
Sử dụng cơ chế `BackgroundTasks` tích hợp sẵn trong FastAPI để chạy các tác vụ định kỳ mà không ảnh hưởng đến luồng phản hồi HTTP chính:
- **Dọn dẹp OTP hết hạn:** Giải phóng tài nguyên cơ sở dữ liệu bằng cách xóa định kỳ các bản ghi OTP đã quá hạn sử dụng.
- **Xóa tài khoản ảo:** Tự động loại bỏ các yêu cầu đăng ký giả lập (những tài khoản không kích hoạt OTP trong vòng 24 giờ).

---

## 5. HƯỚNG DẪN CÀI ĐẶT & HƯỚNG DẪN VẬN HÀNH

### 5.1 Khởi tạo môi trường ảo

**Windows (PowerShell):**
```powershell
cd KeBook-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
cd KeBook-backend
python3 -m venv venv
source venv/bin/activate
```

### 5.2 Cài đặt thư viện phụ thuộc
Sử dụng công cụ quản lý thư viện hiện đại hoặc `pip` truyền thống:
```bash
pip install -r requirements-prod.txt
```

### 5.3 Cấu hình hệ thống thông qua biến môi trường (`.env`)
Tạo một file `.env` tại thư mục gốc backend dựa trên mẫu `.env.example`:
```env
# Cấu hình Kết nối CSDL
DATABASE_URL=mysql+aiomysql://kebook_user:secure_pwd@aiven-cloud-host:3306/kebook

# Bảo mật và Mã hóa
SECRET_KEY=9a1505c8651a2d1d03c21a206be0975e52a4e28e19e7a4b277b056ea02e88a0b
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Máy chủ gửi thư (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=support@kebook.vn
SMTP_PASSWORD=your_app_password
SMTP_FROM_EMAIL=support@kebook.vn

# Cấu hình OTP
OTP_EXPIRE_SECONDS=300
OTP_LENGTH=6
```

### 5.4 Khởi chạy Máy chủ Uvicorn
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Truy cập tài liệu API tự động (Swagger UI): `http://localhost:8000/docs`
- Truy cập tài liệu giao diện ReDoc: `http://localhost:8000/redoc`

---

## 6. KIỂM THỬ VÀ ĐẢM BẢO CHẤT LƯỢNG

### 6.1 Unit Test và Integration Test (`pytest`)
Hệ thống tích hợp bộ kiểm thử tự động toàn diện sử dụng framework `pytest` và `pytest-asyncio` giúp kiểm tra tính đúng đắn của logic xử lý bất đồng bộ.
```bash
pytest -v
```
Bộ test bao gồm việc giả lập (mocking) cơ sở dữ liệu SQLite trong bộ nhớ nhằm kiểm tra nhanh các API:
- Kiểm thử luồng đăng ký, gửi OTP, xác thực và đăng nhập thành công.
- Kiểm thử tính toán giỏ hàng và áp dụng voucher chính xác.
- Kiểm thử phân quyền: đảm bảo user thường không thể truy cập các API dành riêng cho quản trị viên (Admin-only).

### 6.2 Bộ công cụ kiểm thử Postman (Postman Test Kit)
Mã nguồn chứa sẵn bộ sưu tập kiểm thử tích hợp (Integration Collection):
- `postman/Backend_Kebook_API.postman_collection.json`
- `postman/Backend_Kebook_Local.postman_environment.json`

Bộ sưu tập được thiết kế tối ưu hóa với các đoạn mã tiền xử lý (Pre-request Script) và hậu xử lý (Tests) để tự động hóa việc lưu trữ JWT Access Token vào các biến môi trường toàn cục (`user_token`, `admin_token`), giúp nhà phát triển dễ dàng kiểm thử chuỗi API phức tạp chỉ bằng một nút bấm.

---

## 7. KẾT LUẬN

Hệ thống **KeBook Backend** đã chứng minh tính hiệu quả vượt trội trong việc ứng dụng kiến trúc phân tầng kết hợp lập trình bất đồng bộ. Việc tổ chức mã nguồn chuẩn hóa giúp giảm tối đa rủi ro xung đột mã nguồn và tăng cường khả năng bảo trì. Sự kết hợp giữa các giải pháp bảo mật JWT, băm mật khẩu Bcrypt và xác thực OTP Email tạo dựng một nền tảng vững chắc, sẵn sàng đáp ứng tải lượng người dùng lớn trong môi trường thực tế.

---
*Tài liệu thuộc Chương trình Nghiên cứu & Phát triển Hệ thống Web Nâng cao - Dự án KeBook.*
