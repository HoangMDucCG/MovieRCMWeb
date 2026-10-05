import random
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Movie, Genre
from urllib.parse import urlparse, parse_qs
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator


@never_cache
def home_page(request):
    today = date.today()
    hot_movies = Movie.objects.filter(rating__gt=8.0, release_date__lte=today).order_by(
        "-rating"
    )[:10]
    upcoming_movies = Movie.objects.filter(rating=0.0, release_date__gt=today).order_by(
        "release_date"
    )[:10]

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


# XÓA BỎ HOÀN TOÀN HÀM xem_phim(request, id)
