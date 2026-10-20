document.addEventListener("DOMContentLoaded", function () {
    const filterBtn = document.getElementById("filter-button");
    const filterPopup = document.getElementById("filter-popup");
    const applyBtn = document.getElementById("apply-filter");

    if (filterBtn && filterPopup) {
        filterBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            if (filterPopup.style.display === "none" || filterPopup.style.display === "") {
                filterPopup.style.display = "block";
            } else {
                filterPopup.style.display = "none";
            }
        });

        document.addEventListener("click", function (e) {
            if (!filterPopup.contains(e.target) && e.target !== filterBtn) {
                filterPopup.style.display = "none";
            }
        });
    }

    const minRuntime = document.getElementById("min-runtime");
    const maxRuntime = document.getElementById("max-runtime");
    const minRuntimeVal = document.getElementById("min-runtime-value");
    const maxRuntimeVal = document.getElementById("max-runtime-value");

    if (minRuntime && maxRuntime) {
        function updateSlider() {
            let minVal = parseInt(minRuntime.value);
            let maxVal = parseInt(maxRuntime.value);

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

    
    const urlMovieType = params.get("type");
    if (urlMovieType) {
        const typeRadio = document.querySelector(`input[name="movie-type"][value="${urlMovieType}"]`);
        if (typeRadio) typeRadio.checked = true;
    }

    
    const urlGenres = params.getAll("genre");
    if (urlGenres.length > 0) {
        urlGenres.forEach((g) => {
            const genreCheck = document.querySelector(`input[name="genre"][value="${g}"]`);
            if (genreCheck) genreCheck.checked = true;
        });
    }

    
    const urlRating = params.get("min_rating");
    if (urlRating) {
        const ratingSelect = document.getElementById("min-rating");
        if (ratingSelect) ratingSelect.value = urlRating;
    }

    
    const urlMinRuntime = params.get("min_runtime");
    const urlMaxRuntime = params.get("max_runtime");
    
    if (urlMinRuntime && minRuntime) {
        minRuntime.value = urlMinRuntime;
    }
    if (urlMaxRuntime && maxRuntime) {
        maxRuntime.value = urlMaxRuntime;
    }
    
    if (minRuntime && maxRuntime) updateSlider();


    // ====================================================================
    // 4. XỬ LÝ KHI NHẤN NÚT "ÁP DỤNG"
    // ====================================================================
    if (applyBtn) {
        applyBtn.addEventListener("click", function () {
            // Lấy URL đích từ data-url của nút
            const baseUrl = this.getAttribute("data-url") || window.location.pathname;
            const searchParams = new URLSearchParams(window.location.search);

            
            searchParams.delete("type");
            searchParams.delete("genre");
            searchParams.delete("min_rating");
            searchParams.delete("min_runtime");
            searchParams.delete("max_runtime");
            searchParams.delete("page"); 

        
            const typeVal = document.querySelector('input[name="movie-type"]:checked').value;
            if (typeVal !== "") searchParams.append("type", typeVal);

        
            const genreChecks = document.querySelectorAll('input[name="genre"]:checked');
            genreChecks.forEach(cb => searchParams.append("genre", cb.value));

        
            const ratingVal = document.getElementById("min-rating").value;
            if (ratingVal !== "0") searchParams.append("min_rating", ratingVal);

            const minRt = minRuntime.value;
            const maxRt = maxRuntime.value;

            if (minRt !== "30" || maxRt !== "240") {
                searchParams.append("min_runtime", minRt);
                searchParams.append("max_runtime", maxRt);
            }

            const newUrl = baseUrl + "?" + searchParams.toString();
            window.location.href = newUrl;
        });
    }
});