document.addEventListener("DOMContentLoaded", function () {
    const filterBtn = document.getElementById("filter-button");
    const filterPopup = document.getElementById("filter-popup");
    const applyBtn = document.getElementById("apply-filter");

    // 1. TÍNH NĂNG BẬT / TẮT POPUP
    if (filterBtn && filterPopup) {
        filterBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            if (filterPopup.style.display === "none" || filterPopup.style.display === "") {
                filterPopup.style.display = "block";
            } else {
                filterPopup.style.display = "none";
            }
        });

        // Click ra ngoài thì đóng popup
        document.addEventListener("click", function (e) {
            if (!filterPopup.contains(e.target) && e.target !== filterBtn) {
                filterPopup.style.display = "none";
            }
        });
    }

    // 2. KHỞI TẠO THANH KÉO THỜI LƯỢNG (Range Slider)
    const minRuntime = document.getElementById("min-runtime");
    const maxRuntime = document.getElementById("max-runtime");
    const minRuntimeVal = document.getElementById("min-runtime-value");
    const maxRuntimeVal = document.getElementById("max-runtime-value");

    if (minRuntime && maxRuntime) {
        function updateSlider() {
            let minVal = parseInt(minRuntime.value);
            let maxVal = parseInt(maxRuntime.value);

            // Đảm bảo nút Min không vượt qua nút Max
            if (minVal > maxVal) {
                let tmp = minVal;
                minVal = maxVal;
                maxVal = tmp;
            }

            minRuntimeVal.textContent = minVal;
            maxRuntimeVal.textContent = maxVal;
        }

        minRuntime.addEventListener("input", updateSlider);
        maxRuntime.addEventListener("input", updateSlider);
    }

    // ====================================================================
    // 3. TÍNH NĂNG GIỮ LẠI LỰA CHỌN SAU KHI TẢI TRANG (ĐỌC TỪ URL)
    // ====================================================================
    const params = new URLSearchParams(window.location.search);

    // Phục hồi: Loại phim (Radio)
    const urlMovieType = params.get("type");
    if (urlMovieType) {
        const typeRadio = document.querySelector(`input[name="movie-type"][value="${urlMovieType}"]`);
        if (typeRadio) typeRadio.checked = true;
    }

    // Phục hồi: Thể loại (Checkbox) - Có thể chọn nhiều
    const urlGenres = params.getAll("genre");
    if (urlGenres.length > 0) {
        urlGenres.forEach((g) => {
            const genreCheck = document.querySelector(`input[name="genre"][value="${g}"]`);
            if (genreCheck) genreCheck.checked = true;
        });
    }

    // Phục hồi: Rating (Select)
    const urlRating = params.get("min_rating");
    if (urlRating) {
        const ratingSelect = document.getElementById("min-rating");
        if (ratingSelect) ratingSelect.value = urlRating;
    }

    // Phục hồi: Thời lượng (Range Slider)
    const urlMinRuntime = params.get("min_runtime");
    const urlMaxRuntime = params.get("max_runtime");
    
    if (urlMinRuntime && minRuntime) {
        minRuntime.value = urlMinRuntime;
    }
    if (urlMaxRuntime && maxRuntime) {
        maxRuntime.value = urlMaxRuntime;
    }
    // Cập nhật lại hiển thị số phút sau khi gán giá trị
    if (minRuntime && maxRuntime) updateSlider();


    // ====================================================================
    // 4. XỬ LÝ KHI NHẤN NÚT "ÁP DỤNG"
    // ====================================================================
    if (applyBtn) {
        applyBtn.addEventListener("click", function () {
            // Lấy URL đích từ data-url của nút
            const baseUrl = this.getAttribute("data-url") || window.location.pathname;
            const searchParams = new URLSearchParams(window.location.search);

            // Xóa các bộ lọc cũ đi để cập nhật cái mới
            searchParams.delete("type");
            searchParams.delete("genre");
            searchParams.delete("min_rating");
            searchParams.delete("min_runtime");
            searchParams.delete("max_runtime");
            // Luôn reset về trang 1 khi lọc mới
            searchParams.delete("page"); 

            // Thu thập: Loại phim
            const typeVal = document.querySelector('input[name="movie-type"]:checked').value;
            if (typeVal !== "") searchParams.append("type", typeVal);

            // Thu thập: Thể loại (có thể nhiều giá trị)
            const genreChecks = document.querySelectorAll('input[name="genre"]:checked');
            genreChecks.forEach(cb => searchParams.append("genre", cb.value));

            // Thu thập: Rating
            const ratingVal = document.getElementById("min-rating").value;
            if (ratingVal !== "0") searchParams.append("min_rating", ratingVal);

            // Thu thập: Thời lượng
            const minRt = minRuntime.value;
            const maxRt = maxRuntime.value;
            // Nếu không phải khoảng mặc định thì mới thêm vào URL cho gọn
            if (minRt !== "30" || maxRt !== "240") {
                searchParams.append("min_runtime", minRt);
                searchParams.append("max_runtime", maxRt);
            }

            // Chuyển hướng sang URL mới
            const newUrl = baseUrl + "?" + searchParams.toString();
            window.location.href = newUrl;
        });
    }
});