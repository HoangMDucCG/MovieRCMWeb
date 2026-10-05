document.addEventListener("DOMContentLoaded", function() {
    let lastScrollTop = 0;
    const header = document.querySelector(".site-header");

    window.addEventListener("scroll", function() {
        // Lấy vị trí cuộn hiện tại
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        // Nếu cuộn xuống và đã cuộn qua một khoảng (ví dụ 50px để tránh giật lag ở tuốt trên cùng)
        if (scrollTop > lastScrollTop && scrollTop > 50) {
            // Cuộn xuống -> Ẩn header
            header.classList.add("hide-header");
        } else {
            // Cuộn lên -> Hiện header
            header.classList.remove("hide-header");
        }
        
        // Cập nhật lại vị trí cuối cùng
        lastScrollTop = scrollTop;
    });
});