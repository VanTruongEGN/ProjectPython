document.addEventListener("DOMContentLoaded", function () {

    const carousel = document.querySelector("#mainCarousel");
    const items = carousel.querySelectorAll(".carousel-item");
    const btnPrev = carousel.querySelector(".prev");
    const btnNext = carousel.querySelector(".next");

    let index = 0;

    function showSlide(i) {
        items.forEach(item => item.classList.remove("active"));
        items[i].classList.add("active");
    }

    btnNext.addEventListener("click", () => {
        index = (index + 1) % items.length;
        showSlide(index);
    });

    btnPrev.addEventListener("click", () => {
        index = (index - 1 + items.length) % items.length;
        showSlide(index);
    });

    // Auto slide
    setInterval(() => {
        index = (index + 1) % items.length;
        showSlide(index);
    }, 3500);
});
