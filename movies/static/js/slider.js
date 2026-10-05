function slide(sliderId, direction) {
    const slider = document.getElementById(sliderId);
    if (slider) {
        // Tính toán xem thanh trượt đã chạm lề trái hay lề phải chưa
        const isAtEnd = Math.ceil(slider.scrollLeft + slider.clientWidth) >= slider.scrollWidth - 1;
        const isAtStart = slider.scrollLeft <= 0;

        if (direction === 1 && isAtEnd) {
            // Đang ở bộ phim cuối cùng mà bấm Next -> Cuộn mượt mà về vị trí 0 (đầu tiên)
            slider.scrollTo({ left: 0, behavior: 'smooth' });
        } 
        else if (direction === -1 && isAtStart) {
            // Đang ở bộ phim đầu tiên mà bấm Prev -> Vòng ngược lại bộ phim cuối cùng
            slider.scrollTo({ left: slider.scrollWidth, behavior: 'smooth' });
        } 
        else {
            // Nếu nằm ở giữa thì cứ trượt qua lại 300px bình thường
            slider.scrollBy({ left: 250 * direction, behavior: 'smooth' });
        }
    }
}

// 2. Thêm mới: Hàm kiểm tra lề để bật/tắt viền mờ
function updateFadeEdges() {
    const sliders = document.querySelectorAll(".movie-slider");

    sliders.forEach((slider) => {
        const isAtStart = slider.scrollLeft <= 0;
        const isAtEnd =
            Math.ceil(slider.scrollLeft + slider.clientWidth) >=
            slider.scrollWidth - 1;

        if (isAtStart) {
            slider.classList.add("at-start");
            slider.classList.remove("at-end");
        } else if (isAtEnd) {
            slider.classList.add("at-end");
            slider.classList.remove("at-start");
        } else {
            slider.classList.remove("at-start", "at-end");
        }
    });
}

// 3. Thêm mới: Chạy kiểm tra ngay khi web tải xong và khi cuộn
document.addEventListener("DOMContentLoaded", () => {
    updateFadeEdges(); // Chạy 1 lần đầu tiên để nhận diện lề trái

    // Lắng nghe sự kiện cuộn trên tất cả các thanh trượt
    document.querySelectorAll(".movie-slider").forEach((slider) => {
        slider.addEventListener("scroll", updateFadeEdges);
    });
});
