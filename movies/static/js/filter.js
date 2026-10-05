document.addEventListener("DOMContentLoaded", function () {
    // ==============================
    // 1. MỞ / ĐÓNG POPUP LỌC
    // ==============================
    const filterButton = document.getElementById("filter-button");
    const filterPopup = document.getElementById("filter-popup");

    if (filterButton && filterPopup) {
        filterButton.addEventListener("click", function (e) {
            e.stopPropagation();
            filterPopup.style.display =
                filterPopup.style.display === "block" ? "none" : "block";
        });

        document.addEventListener("click", function (e) {
            if (
                !filterPopup.contains(e.target) &&
                !filterButton.contains(e.target)
            ) {
                filterPopup.style.display = "none";
            }
        });
    }

    // ==============================
    // 2. XỬ LÝ THANH TRƯỢT THỜI LƯỢNG
    // ==============================
    const minRuntime = document.getElementById("min-runtime");
    const maxRuntime = document.getElementById("max-runtime");
    const minRuntimeValue = document.getElementById("min-runtime-value");
    const maxRuntimeValue = document.getElementById("max-runtime-value");

    if (minRuntime && maxRuntime) {
        minRuntime.addEventListener("input", function () {
            if (parseInt(minRuntime.value) >= parseInt(maxRuntime.value)) {
                minRuntime.value = parseInt(maxRuntime.value) - 1;
            }
            if (minRuntimeValue) minRuntimeValue.textContent = minRuntime.value;
        });

        maxRuntime.addEventListener("input", function () {
            if (parseInt(maxRuntime.value) <= parseInt(minRuntime.value)) {
                maxRuntime.value = parseInt(minRuntime.value) + 1;
            }
            if (maxRuntimeValue) maxRuntimeValue.textContent = maxRuntime.value;
        });
    }

    // ==============================
    // 3. ÁP DỤNG BỘ LỌC
    // ==============================
    const applyFilter = document.getElementById("apply-filter");

    if (applyFilter) {
        applyFilter.addEventListener("click", function () {
            const params = new URLSearchParams();

            // Lấy từ khóa tìm kiếm
            const searchInput = document.getElementById("search-input");
            if (searchInput && searchInput.value.trim() !== "") {
                params.set("q", searchInput.value.trim());
            }

            // Lấy loại phim
            const movieType = document.querySelector(
                'input[name="movie-type"]:checked',
            );
            if (movieType && movieType.value !== "") {
                params.set("type", movieType.value);
            }

            // Lấy thể loại
            const selectedGenres = document.querySelectorAll(
                'input[name="genre"]:checked',
            );
            selectedGenres.forEach(function (checkbox) {
                params.append("genre", checkbox.value);
            });

            // Lấy rating
            const minRating = document.getElementById("min-rating");
            if (minRating && minRating.value !== "0") {
                params.set("min_rating", minRating.value);
            }

            // Lấy thời lượng (Sửa lỗi: Đọc giá trị trực tiếp tại thời điểm click)
            if (minRuntime && maxRuntime) {
                if (minRuntime.value !== "30" || maxRuntime.value !== "240") {
                    params.set("min_runtime", minRuntime.value);
                    params.set("max_runtime", maxRuntime.value);
                }
            }

            // Lấy đường dẫn URL từ thuộc tính data-url của nút bấm
            const searchUrl = applyFilter.getAttribute("data-url");

            // Chuyển hướng
            if (searchUrl) {
                window.location.href = searchUrl + "?" + params.toString();
            }
        });
    }
});
