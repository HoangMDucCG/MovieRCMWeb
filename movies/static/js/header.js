document.addEventListener("DOMContentLoaded", function() {
    let lastScrollTop = 0;
    const header = document.querySelector(".site-header");

    window.addEventListener("scroll", function() {
        let scrollTop = window.pageYOffset || document.documentElement.scrollTop;

        if (scrollTop > lastScrollTop && scrollTop > 50) {
            // Cuộn xuống -> Ẩn header
            header.classList.add("hide-header");
        } else {
            header.classList.remove("hide-header");
        }
        
        lastScrollTop = scrollTop;
    });
});