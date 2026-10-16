import json
from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie, Genre
from .views import ai_client


class WebPhimMoiSystemTestCase(TestCase):
    def setUp(self):
        """Khởi tạo dữ liệu giả lập chuẩn theo models.py hiện tại."""
        self.client = Client()

        # 1. Tạo Thể Loại
        self.genre_hanh_dong = Genre.objects.create(name="Hành Động")
        self.genre_hai_huoc = Genre.objects.create(name="Hài Hước")
        self.genre_tinh_cam = Genre.objects.create(name="Tình Cảm")

        # Ngày hiện tại, quá khứ và tương lai
        today = date.today()
        past_date = today - timedelta(days=30)
        future_date = today + timedelta(days=30)

        # 2. Tạo Phim Lẻ (Hành Động + Hài Hước, Hot)
        self.movie_le = Movie.objects.create(
            title="Avengers: Hồi Kết",
            type="Phim Lẻ",
            rating=9.5,
            release_date=past_date,
            runtime_minutes=180,
            poster_url="https://example.com/poster1.jpg",
            trailer="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            description="Mô tả phim Avengers"
        )
        self.movie_le.genres.add(self.genre_hanh_dong, self.genre_hai_huoc)

        # 3. Tạo Phim Bộ (Chỉ Hành Động, Rating thấp)
        self.movie_bo = Movie.objects.create(
            title="Wednesday",
            type="Phim Bộ",
            rating=7.5,
            release_date=past_date,
            runtime_minutes=45,
            description="Mô tả phim Wednesday"
        )
        self.movie_bo.genres.add(self.genre_hanh_dong)

        # 4. Tạo Phim Sắp Chiếu
        self.movie_sap_chieu = Movie.objects.create(
            title="Avatar 3",
            type="Phim Lẻ",
            rating=0.0,
            release_date=future_date,
            runtime_minutes=190,
            description="Mô tả phim Avatar 3"
        )

    # =========================================================================
    # 1. KIỂM TRA CÁC TRANG TẢI GIAO DIỆN CHÍNH
    # =========================================================================
    def test_home_page_status_code(self):
        """Kiểm tra trang chủ tải thành công."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('new_movies', response.context)
        self.assertIn('hot_movies', response.context)

    def test_phim_le_page(self):
        """Kiểm tra trang Phim Lẻ chỉ chứa Phim Lẻ."""
        response = self.client.get(reverse('phim_le'))
        self.assertEqual(response.status_code, 200)
        movies = response.context['movies']
        self.assertTrue(all(m.type == 'Phim Lẻ' for m in movies))

    def test_phim_bo_page(self):
        """Kiểm tra trang Phim Bộ chỉ chứa Phim Bộ."""
        response = self.client.get(reverse('phim_bo'))
        self.assertEqual(response.status_code, 200)
        movies = response.context['movies']
        self.assertTrue(all(m.type == 'Phim Bộ' for m in movies))

    def test_the_loai_page(self):
        """Kiểm tra lọc theo thể loại trên URL."""
        response = self.client.get(reverse('the_loai') + '?ten=Hành Động')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['movies']), 2)

    # =========================================================================
    # 2. KIỂM TRA CHI TIẾT PHIM VÀ CHUYỂN HƯỚNG NGẪU NHIÊN
    # =========================================================================
    def test_xem_series_detail(self):
        """Kiểm tra trang chi tiết phim tồn tại và 404 nếu sai ID."""
        response = self.client.get(reverse('xem_series', args=[self.movie_le.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['series'], self.movie_le)

        # ID không tồn tại phải trả về 404
        response_404 = self.client.get(reverse('xem_series', args=[99999]))
        self.assertEqual(response_404.status_code, 404)

    def test_ngau_nhien_redirect(self):
        """Kiểm tra nút Ngẫu nhiên phải chuyển hướng sang trang chi tiết phim."""
        response = self.client.get(reverse('ngau_nhien'))
        self.assertEqual(response.status_code, 302)  # Chuyển hướng 302

    # =========================================================================
    # 3. KIỂM TRA LOGIC BỘ LỌC TÌM KIẾM (SEARCH & FILTER)
    # =========================================================================
    def test_search_by_keyword(self):
        """Tìm kiếm theo từ khóa tên phim."""
        response = self.client.get(reverse('search') + '?q=Avengers')
        self.assertEqual(len(response.context['movies']), 1)
        self.assertEqual(response.context['movies'][0].title, "Avengers: Hồi Kết")

    def test_search_by_type_and_rating(self):
        """Lọc theo Loại phim và Rating tối thiểu."""
        response = self.client.get(reverse('search') + '?type=Phim+Lẻ&min_rating=8.0')
        self.assertEqual(len(response.context['movies']), 1)
        self.assertEqual(response.context['movies'][0].title, "Avengers: Hồi Kết")

    def test_search_by_runtime_range(self):
        """Lọc theo khoảng thời lượng min_runtime và max_runtime."""
        response = self.client.get(reverse('search') + '?min_runtime=30&max_runtime=60')
        self.assertEqual(len(response.context['movies']), 1)
        self.assertEqual(response.context['movies'][0].title, "Wednesday")

    def test_search_by_multiple_genres_and_logic(self):
        """Kiểm tra logic lọc VÀ (AND): Phim phải chứa đủ TẤT CẢ thể loại chọn."""
        url = reverse('search') + '?genre=Hành+Động&genre=Hài+Hước'
        response = self.client.get(url)
        movies = response.context['movies']
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].title, "Avengers: Hồi Kết")

        url_no_match = reverse('search') + '?genre=Hành+Động&genre=Tình+Cảm'
        response_no_match = self.client.get(url_no_match)
        self.assertEqual(len(response_no_match.context['movies']), 0)

    # =========================================================================
    # 4. KIỂM TRA LIVE SEARCH API (JSON)
    # =========================================================================
    def test_live_search_api(self):
        """Kiểm tra API gợi ý tìm kiếm tức thì."""
        # Đổi chữ 'Av' thành 'Avengers' để chỉ tìm ra đúng 1 phim
        response = self.client.get(reverse('live_search') + '?q=Avengers')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], "Avengers: Hồi Kết")

    # =========================================================================
    # 5. KIỂM TRA API CHATBOT AI (MOCK GEMINI API)
    # =========================================================================
    @patch.object(ai_client.models, 'generate_content')
    def test_chatbot_api_success(self, mock_generate_content):
        """Kiểm tra API Chatbot phản hồi JSON khi gửi tin nhắn hợp lệ."""
        mock_response = MagicMock()
        mock_response.text = "Chào bạn! Đây là gợi ý phim **Avengers: Hồi Kết**."
        mock_generate_content.return_value = mock_response

        payload = {
            "message": "Tư vấn cho mình phim hành động hay",
            "history": [
                {"role": "user", "content": "Xin chào"},
                {"role": "bot", "content": "Chào bạn!"}
            ]
        }

        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reply", data)

    def test_chatbot_api_empty_message(self):
        """Kiểm tra gửi tin nhắn rỗng tới Chatbot."""
        payload = {"message": "", "history": []}
        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Bạn muốn mình tư vấn", response.json()["reply"])