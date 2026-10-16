import json
import random
from datetime import date
from urllib.parse import urlparse, parse_qs

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from google import genai
from google.genai import types

from .models import Movie, Genre

# ==============================================================================
# CẤU HÌNH API
# ==============================================================================

API_KEY = ""
ai_client = genai.Client(api_key=API_KEY)


# ==============================================================================
# 1. TRANG CHỦ VÀ DANH MỤC CHÍNH
# ==============================================================================

@never_cache
def home_page(request):
    """Trang chủ hiển thị Phim Hot, Phim Sắp Chiếu và Phim Mới Cập Nhật."""
    today = date.today()
    hot_movies = Movie.objects.filter(rating__gt=8.0, release_date__lte=today).order_by("-rating")[:10]
    upcoming_movies = Movie.objects.filter(release_date__gt=today).order_by("release_date")
    new_movies_list = Movie.objects.filter(release_date__lte=today).order_by("-release_date")

    paginator = Paginator(new_movies_list, 25)
    page_number = request.GET.get("page")
    new_movies = paginator.get_page(page_number)

    context = {
        "upcoming_movies": upcoming_movies,
        "hot_movies": hot_movies,
        "new_movies": new_movies,
        "categories": Genre.objects.all(),
    }
    return render(request, "movies/home.html", context)


def the_loai(request):
    """Lọc phim theo Thể loại (Genre)."""
    ten_the_loai = request.GET.get("ten")
    ket_qua_phim = (
        Movie.objects.filter(genres__name=ten_the_loai).distinct().order_by("-release_date")
        if ten_the_loai else Movie.objects.none()
    )

    paginator = Paginator(ket_qua_phim, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    # Giữ lại tham số url khi chuyển trang
    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    context = {
        "movies": movies_page,
        "categories": Genre.objects.all(),
        "tieu_de_muc": ten_the_loai,
        "query_string": query_dict.urlencode(),
    }
    return render(request, "movies/the_loai.html", context)


def phim_le(request):
    """Danh sách tất cả Phim Lẻ."""
    danh_sach_phim = Movie.objects.filter(type="Phim Lẻ").order_by("-release_date")
    
    paginator = Paginator(danh_sach_phim, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    context = {
        "movies": movies_page,
        "categories": Genre.objects.all(),
    }
    return render(request, "movies/phim_le.html", context)


def phim_bo(request):
    """Danh sách tất cả Phim Bộ."""
    danh_sach_phim = Movie.objects.filter(type="Phim Bộ").order_by("-release_date")
    
    paginator = Paginator(danh_sach_phim, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    context = {
        "movies": movies_page,
        "categories": Genre.objects.all(),
    }
    return render(request, "movies/phim_bo.html", context)


# ==============================================================================
# 2. TÌM KIẾM VÀ LỌC (SEARCH & FILTER)
# ==============================================================================

def search_movie(request):
    """Tìm kiếm nâng cao kết hợp bộ lọc (Tên, Loại, Thể loại, Rating, Thời lượng)."""
    query = request.GET.get("q", "").strip()
    movie_type = request.GET.get("type", "").strip()
    genre_filters = request.GET.getlist("genre")
    min_rating = request.GET.get("min_rating", "").strip()
    min_runtime = request.GET.get("min_runtime", "").strip()
    max_runtime = request.GET.get("max_runtime", "").strip()

    movies = Movie.objects.all().order_by("-id")

    # Lọc theo tên
    if query:
        movies = movies.filter(title__icontains=query)

    # Lọc theo loại phim (Lẻ/Bộ)
    if movie_type:
        movies = movies.filter(type=movie_type)

    # Lọc theo thể loại (AND)
    if genre_filters:
        for genre in genre_filters:
            movies = movies.filter(genres__name=genre)
        movies = movies.distinct()

    # Lọc theo Rating tối thiểu
    if min_rating:
        try:
            if float(min_rating) > 0:
                movies = movies.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    # Lọc theo Khoảng thời lượng
    if min_runtime:
        try:
            movies = movies.filter(runtime_minutes__gte=int(min_runtime))
        except ValueError:
            pass
    if max_runtime:
        try:
            movies = movies.filter(runtime_minutes__lte=int(max_runtime))
        except ValueError:
            pass

    # Giữ lại URL params cho phân trang
    query_dict = request.GET.copy()
    if "page" in query_dict:
        del query_dict["page"]

    paginator = Paginator(movies, 25)
    page_number = request.GET.get("page")
    movies_page = paginator.get_page(page_number)

    context = {
        "movies": movies_page,
        "query_string": query_dict.urlencode(),
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
    """Gợi ý tìm kiếm tức thì trả về JSON."""
    query = request.GET.get("q", "").strip()
    if query:
        movies = Movie.objects.filter(title__icontains=query)[:5]
        results = [{
            "title": m.title,
            "poster_url": m.poster_url,
            "year": m.release_date.year if m.release_date else "N/A",
            "url": reverse("xem_series", args=[m.id]),
        } for m in movies]
        return JsonResponse({"results": results})
    return JsonResponse({"results": []})


# ==============================================================================
# 3. TRANG CHI TIẾT VÀ TÍNH NĂNG PHỤ
# ==============================================================================

def ngau_nhien(request):
    """Chuyển hướng ngẫu nhiên đến một phim bất kỳ."""
    movies = list(Movie.objects.values_list('id', flat=True))
    if movies:
        return redirect("xem_series", id=random.choice(movies))
    return redirect("home")


def get_youtube_id(url):
    """Trích xuất ID Video YouTube từ URL để nhúng iframe."""
    if not url: return None
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
        if parsed_url.path.startswith("/embed/"):
            return parsed_url.path.split("/embed/")[1]
            
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")
    return None


def xem_series(request, id):
    """Trang chi tiết của một bộ phim."""
    phim = get_object_or_404(Movie, id=id)
    online_links = phim.theater_links.filter(theater_name="Netflix")
    theater_links = phim.theater_links.exclude(theater_name="Netflix")

    context = {
        "series": phim,
        "categories": Genre.objects.all(),
        "trailer_id": get_youtube_id(phim.trailer),
        "online_links": online_links,
        "theater_links": theater_links,
    }
    return render(request, "movies/series_detail.html", context)


# ==============================================================================
# 4. CHATBOT AI API (GEMINI)
# ==============================================================================

@csrf_exempt
def chatbot_api(request):
    """API giao tiếp giữa Chatbot Frontend và Gemini Backend."""
    if request.method != "POST":
        return JsonResponse({"reply": "Yêu cầu không hợp lệ"}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        chat_history = data.get("history", [])

        if not user_message:
            return JsonResponse({"reply": "Bạn muốn mình tư vấn phim gì nào?"})

        today = date.today()
        phim_db = Movie.objects.prefetch_related("genres", "theater_links").order_by("-release_date")
        
        # Tạo cơ sở dữ liệu phim dạng Text cho Prompt
        chi_tiet_phim = []
        for p in phim_db:
            the_loai = ", ".join([g.name for g in p.genres.all()]) if p.genres.exists() else "Chưa rõ"
            trang_thai = ["Sắp chiếu" if p.release_date and p.release_date > today else "Đã ra mắt"]
            if p.rating > 8.0: trang_thai.append("Phim Hot🔥")
            
            noi_xem = [link.theater_name for link in p.theater_links.all()]
            
            info = (
                f"- Tên phim: {p.title} | Loại: {getattr(p, 'type', 'N/A')} | Thể loại: {the_loai} | "
                f"Đánh giá: {p.rating}/10 | Thời lượng: {getattr(p, 'runtime_minutes', 'N/A')} phút | "
                f"Trạng thái: {', '.join(trang_thai)} | "
                f"Xem tại: {', '.join(noi_xem) if noi_xem else 'Chưa có thông tin'} | "
                f"Mô tả: {getattr(p, 'description', '')[:200]}..."
            )
            chi_tiet_phim.append(info)

        luat_choi = f"""
        Bạn là trợ lý ảo CSKH cực kỳ chuyên nghiệp của WebPHIMMOI.
        Nhiệm vụ: Tư vấn phim CHỈ DỰA TRÊN CƠ SỞ DỮ LIỆU ĐƯỢC CUNG CẤP DƯỚI ĐÂY. Tuyệt đối không bịa phim.
        
        CƠ SỞ DỮ LIỆU PHIM:
        {chr(10).join(chi_tiet_phim)}
        
        QUY TẮC:
        1. Trả lời theo ngữ cảnh lịch sử chat.
        2. LUÔN in đậm tên phim bằng dấu sao (**Tên phim**).
        3. Nếu liệt kê nhiều phim, PHẢI dùng gạch đầu dòng (-).
        4. Trả lời ngắn gọn, thân thiện, xưng "mình" và gọi "bạn".
        """

        # Format history cho Google GenAI SDK
        formatted_contents = [
            types.Content(
                role="user" if msg["role"] == "user" else "model",
                parts=[types.Part.from_text(text=msg["content"])]
            ) for msg in chat_history[:-1]
        ]
        formatted_contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        )

        response = ai_client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=formatted_contents,
            config=types.GenerateContentConfig(system_instruction=luat_choi),
        )

        return JsonResponse({"reply": response.text})

    except Exception as e:
        print("Chatbot Error:", e)
        return JsonResponse({"reply": "Hệ thống AI hiện đang nghỉ ngơi một chút, thử lại sau nhé!"}, status=500)