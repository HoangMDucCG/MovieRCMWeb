function slide(sliderId, direction) {
    const slider = document.getElementById(sliderId);
    if (slider) {
        const isAtEnd = Math.ceil(slider.scrollLeft + slider.clientWidth) >= slider.scrollWidth - 1;
        const isAtStart = slider.scrollLeft <= 0;

        if (direction === 1 && isAtEnd) {
            slider.scrollTo({ left: 0, behavior: 'smooth' });
        } 
        else if (direction === -1 && isAtStart) {
            slider.scrollTo({ left: slider.scrollWidth, behavior: 'smooth' });
        } 
        else {
            slider.scrollBy({ left: 250 * direction, behavior: 'smooth' });
        }
    }
}

function updateFadeEdges() {
    const sliders = document.querySelectorAll(".movie-slider");

    sliders.forEach((slider) => {
        const isAtStart = slider.scrollLeft <= 0;
        const isAtEnd =
            Math.ceil(slider.scrollLeft + slider.clientWidth) >=
            slider.scrollWidth - 1;

        const hasOverflow = slider.scrollWidth > slider.clientWidth+1;
        
        const container = slider.parentElement;
        const prevBtn = container.querySelector(".prev-btn");
        const nextBtn = container.querySelector(".next-btn");

        if (prevBtn) {
            prevBtn.style.display = hasOverflow ? "block" : "none";
        }

        if (nextBtn) {
            nextBtn.style.display = hasOverflow ? "block" : "none";
        }
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

document.addEventListener("DOMContentLoaded", () => {
    updateFadeEdges();

    document.querySelectorAll(".movie-slider").forEach((slider) => {
        slider.addEventListener("scroll", updateFadeEdges);
    });
});

window.addEventListener("resize", updateFadeEdges);