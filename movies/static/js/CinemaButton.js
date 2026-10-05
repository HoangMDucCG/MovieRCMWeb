
// =========================================
// POPUP RẠP ĐANG CHIẾU
// =========================================

const theaterBtn = document.getElementById("theaterBtn");
const theaterModal = document.getElementById("theaterModal");
const theaterClose = document.getElementById("theaterClose");


theaterBtn.addEventListener("click", function () {
    theaterModal.classList.add("active");
});


theaterClose.addEventListener("click", function () {
    theaterModal.classList.remove("active");
});


// =========================================
// CLICK RA NGOÀI POPUP ĐỂ ĐÓNG
// =========================================

document.querySelectorAll(".watch-modal-overlay").forEach(function (overlay) {

    overlay.addEventListener("click", function () {

        overlay.parentElement.classList.remove("active");

    });

});


// =========================================
// NHẤN ESC ĐỂ ĐÓNG POPUP
// =========================================

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {

        document.querySelectorAll(".watch-modal").forEach(function (modal) {

            modal.classList.remove("active");

        });

    }

});