import json
import random
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Genre
from urllib.parse import urlparse, parse_qs
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator
from google import genai
from google.genai import types

API_KEY = ""
ai_client = genai.Client(api_key=API_KEY)


@never_cache
def home_page(request):
    today = date.today()
    hot_movies = Movie.objects.filter(rating__gt=8.0, release_date__lte=today).order_by(
        "-rating"
    )[:10]
    upcoming_movies = Movie.objects.filter(release_date__gt=today).order_by(
        "release_date"
    )

    # Lấy toàn bộ phim mới
    new_movies_list = Movie.objects.filter(release_date__lte=today).order_by(
        "-release_date"
    )

    # Phân trang: 25 phim mỗi trang (5 dòng x 5 cột)
    paginator = Paginator(new_movies_list, 25)
    page_number = request.GET.get("page")
    new_movies = paginator.get_page(page_number)

    danh_sach_the_loai = Genre.objects.all()

    context = {
        "upcoming_movies": upcoming_movies,
        "hot_movies": hot_movies,
        "new_movies": new_movies,  # Bây giờ biến này đã mang theo dữ liệu phân trang
        "categories": danh_sach_the_loai,
    }
    return render(request, "movies/home.html", context)


def the_loai(request):
    ten_the_loai_duoc_chon = request.GET.get("ten")

    danh_sach_the_loai = Genre.objects.all()

    if ten_the_loai_duoc_chon:
        ket_qua_phim = (
            Movie.objects.filter(genres__name=ten_the_loai_duoc_chon)
            .distinct()
            .order_by("-release_date")
        )
    else:
        ket_qua_phim = Movie.objects.none()

    context = {
        "movies": ket_qua_phim,
        "categories": danh_sach_the_loai,
        "tieu_de_muc": ten_the_loai_duoc_chon,
    }

    return render(request, "movies/the_loai.html", context)


def search_movie(request):
    # ==============================
    # LẤY DỮ LIỆU TỪ URL
    # ==============================

    query = request.GET.get("q", "").strip()

    movie_type = request.GET.get("type", "").strip()

    genre_filters = request.GET.getlist("genre")

    min_rating = request.GET.get("min_rating", "").strip()

    min_runtime = request.GET.get("min_runtime", "").strip()

    max_runtime = request.GET.get("max_runtime", "").strip()

    # ==============================
    # LẤY TOÀN BỘ PHIM
    # ==============================

    movies = Movie.objects.all().order_by("-id")

    # ==============================
    # 1. LỌC THEO TÊN
    # ==============================

    if query:
        movies = movies.filter(title__icontains=query)

    # ==============================
    # 2. LỌC THEO LOẠI PHIM
    # ==============================

    if movie_type:
        movies = movies.filter(type=movie_type)

    # ==============================
    # 3. LỌC THEO THỂ LOẠI
    # OR
    # Chỉ cần thuộc 1 trong các thể loại
    # được chọn là được
    # ==============================

    if genre_filters:
        movies = movies.filter(genres__name__in=genre_filters).distinct()

    # ==============================
    # 4. LỌC THEO RATING
    # ==============================

    if min_rating:
        try:
            min_rating_value = float(min_rating)

            if min_rating_value > 0:
                movies = movies.filter(rating__gte=min_rating_value)

        except ValueError:
            pass

    # ==============================
    # 5. LỌC THỜI LƯỢNG TỐI THIỂU
    # ==============================

    if min_runtime:
        try:
            min_runtime_value = int(min_runtime)

            movies = movies.filter(runtime_minutes__gte=min_runtime_value)

        except ValueError:
            pass

    # ==============================
    # 6. LỌC THỜI LƯỢNG TỐI ĐA
    # ==============================

    if max_runtime:
        try:
            max_runtime_value = int(max_runtime)

            movies = movies.filter(runtime_minutes__lte=max_runtime_value)

        except ValueError:
            pass

    # ==============================
    # 7. XỬ LÝ PHÂN TRANG VÀ GIỮ BỘ LỌC
    # ==============================

    # Lấy toàn bộ tham số hiện tại trên URL (q, type, genre...) và loại bỏ biến 'page' cũ
    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]
    query_string = query_dict.urlencode()  # Ép thành chuỗi dạng q=batman&type=Phim+Lẻ

    # Phân trang: 25 phim mỗi trang
    paginator = Paginator(movies, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    # ==============================
    # GỬI DỮ LIỆU RA HTML
    # ==============================

    context = {
        "movies": movies_page,  # Truyền dữ liệu đã cắt trang
        "query_string": query_string,  # Truyền chuỗi bộ lọc ra để gắn vào link phân trang
        "categories": Genre.objects.all(),
        "query": query,
        "selected_type": movie_type,
        "selected_genres": genre_filters,
        "selected_rating": min_rating,
        "selected_min_runtime": min_runtime,
        "selected_max_runtime": max_runtime,
    }

    return render(request, "movies/search.html", context)


def live_search(request):
    query = request.GET.get("q", "").strip()
    if query:
        # Lấy tối đa 5 kết quả khớp nhất
        movies = Movie.objects.filter(title__icontains=query)[:5]
        results = []
        for m in movies:
            results.append(
                {
                    "title": m.title,
                    "poster_url": m.poster_url,
                    # Lấy năm khởi chiếu (nếu có)
                    "year": m.release_date.year if m.release_date else "N/A",
                    # Tự động tạo link chuyển đến trang chi tiết phim
                    "url": reverse("xem_series", args=[m.id]),
                }
            )
        return JsonResponse({"results": results})
    return JsonResponse({"results": []})


def phim_le(request):
    # 1. Lấy toàn bộ danh sách phim lẻ
    danh_sach_phim = Movie.objects.filter(type="Phim Lẻ").order_by("-release_date")

    # 2. Cấu hình phân trang (25 phim / 1 trang)
    paginator = Paginator(danh_sach_phim, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    danh_sach_the_loai = Genre.objects.all()

    context = {
        "movies": movies_page,  # Đưa dữ liệu đã cắt trang ra ngoài giao diện
        "categories": danh_sach_the_loai,
    }
    return render(request, "movies/phim_le.html", context)


def phim_bo(request):
    # 1. Lấy toàn bộ danh sách phim bộ
    danh_sach_phim = Movie.objects.filter(type="Phim Bộ").order_by("-release_date")

    # 2. Cấu hình phân trang (25 phim / 1 trang)
    paginator = Paginator(danh_sach_phim, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    danh_sach_the_loai = Genre.objects.all()

    context = {
        "movies": movies_page,  # Đưa dữ liệu đã cắt trang ra ngoài giao diện
        "categories": danh_sach_the_loai,
    }
    return render(request, "movies/phim_bo.html", context)


def ngau_nhien(request):
    movies = list(Movie.objects.all())

    if movies:
        movie = random.choice(movies)
        return redirect("xem_series", id=movie.id)

    return redirect("home")


def get_youtube_id(url):
    if not url:
        return None

    parsed_url = urlparse(url)

    # youtube.com/watch?v=...
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]

        # youtube.com/embed/...
        if parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/embed/")[1]

    # youtu.be/...
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    return None


def xem_series(request, id):
    phim_hien_tai = get_object_or_404(Movie, id=id)
    danh_sach_the_loai = Genre.objects.all()
    trailer_id = get_youtube_id(phim_hien_tai.trailer)

    online_links = phim_hien_tai.theater_links.filter(theater_name="Netflix")

    theater_links = phim_hien_tai.theater_links.exclude(theater_name="Netflix")

    context = {
        "series": phim_hien_tai,
        "categories": danh_sach_the_loai,
        "trailer_id": trailer_id,
        "online_links": online_links,
        "theater_links": theater_links,
    }

    return render(request, "movies/series_detail.html", context)


def phim_dang_chieu(request):
    # Lọc ra những phim có trường is_chieu_rap = True (Giống như đợt trước bạn lọc phim lẻ/bộ bằng số tập)
    movies = Movie.objects.filter(is_chieu_rap=True)

    # Trả về một template (ví dụ: phim_dang_chieu.html) kèm theo danh sách phim đã lọc
    return render(request, "movies/phim_dang_chieu.html", {"movies": movies})


def view_phim_sap_chieu(request):
    today = date.today()
    movies = Movie.objects.filter(release_date__gt=today)
    return render(request, "movies/phim_sap_chieu.html", {"movies": movies})


def view_phim_hot(request):
    movies = Movie.objects.order_by("-rating")

    # Mẹo: Nếu chỉ muốn lấy Top 10 phim hot nhất trang chủ, bạn dùng slice như sau:
    # movies = Movie.objects.order_by('-rating')[:10]

    return render(request, "movies/phim_hot.html", {"movies": movies})


def chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()

            if not user_message:
                return JsonResponse({"reply": "Bạn muốn mình tư vấn phim gì nào?"})

            today = date.today()

            # 1. Lấy 50 phim mới nhất kèm Thể loại và Link rạp (Dùng prefetch_related để web không bị giật lag)
            phim_db = Movie.objects.prefetch_related(
                "genres", "theater_links"
            ).order_by("-release_date")

            chi_tiet_phim = []
            for p in phim_db:
                # Lọc Thể loại
                the_loai = (
                    ", ".join([g.name for g in p.genres.all()])
                    if p.genres.exists()
                    else "Chưa rõ"
                )

                # Lọc Trạng thái (Sắp chiếu / Đã chiếu / Đang chiếu rạp / Phim Hot)
                trang_thai = []
                if p.release_date and p.release_date > today:
                    trang_thai.append(
                        f"Sắp chiếu (Dự kiến: {p.release_date.strftime('%d/%m/%Y')})"
                    )
                else:
                    trang_thai.append("Đã ra mắt")

                if getattr(p, "is_chieu_rap", False):
                    trang_thai.append("Đang chiếu rạp")
                if p.rating > 8.0:
                    trang_thai.append("Phim Hot🔥")

                # Lọc Nơi xem (Rạp CGV, Lotte... hoặc Online như Netflix)
                noi_xem = [link.theater_name for link in p.theater_links.all()]
                noi_xem_str = (
                    ", ".join(noi_xem) if noi_xem else "Chưa có thông tin nền tảng"
                )

                # Đóng gói thành 1 câu hoàn chỉnh cho AI đọc
                info = f"- Tên phim: {p.title} | Thể loại: {the_loai} | Đánh giá: {p.rating}/10 | Trạng thái: {', '.join(trang_thai)} | Có thể xem tại: {noi_xem_str}"
                chi_tiet_phim.append(info)

            danh_sach_phim = "\n".join(chi_tiet_phim)

            # 2. Huấn luyện lại "Bộ não" để AI biết cách dùng dữ liệu mới
            luat_choi = """
            Bạn là trợ lý ảo CSKH cực kỳ chuyên nghiệp của WebPHIMMOI.
            Nhiệm vụ: Tư vấn phim CHỈ DỰA TRÊN danh sách được cung cấp. Tuyệt đối không bịa phim ngoài danh sách.
            
            QUY TẮC TRÌNH BÀY BẮT BUỘC (RẤT QUAN TRỌNG):
            1. LUÔN in đậm tên phim bằng dấu sao (Ví dụ: **Avengers: Hồi Kết**).
            2. Nếu liệt kê nhiều phim, PHẢI dùng dấu gạch ngang (-) ở đầu dòng và mỗi phim nằm trên 1 dòng riêng biệt.
            3. Giãn cách các đoạn văn bằng 1 dòng trống để khách dễ đọc.
            4. Luôn trả lời ngắn gọn, thân thiện, xưng "mình" và gọi khách là "bạn".

            - Nếu khách hỏi "phim chiếu rạp", hãy tìm phim có chữ "Đang chiếu rạp".
            - Nếu khách hỏi "xem online", hãy tìm phim có nền tảng như "Netflix" ở mục "Có thể xem tại".
            - Nếu khách hỏi rạp cụ thể (VD: CGV, Lotte), hãy dò đúng tên rạp trong mục "Có thể xem tại".
            """

            # 3. Gửi cục dữ liệu siêu chi tiết này cho Gemini
            prompt = f"DANH SÁCH PHIM HIỆN CÓ:\n{danh_sach_phim}\n\nCâu hỏi của khách: {user_message}"

            response = ai_client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=luat_choi,
                ),
            )

            return JsonResponse({"reply": response.text})

        except Exception as e:
            return JsonResponse(
                {
                    "reply": "Hệ thống AI hiện đang nghỉ ngơi một chút, bạn thử lại sau vài phút nhé!"
                },
                status=500,
            )

    return JsonResponse({"reply": "Yêu cầu không hợp lệ"}, status=400)
