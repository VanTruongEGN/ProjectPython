function changeImage(img) {
    document.getElementById('mainImage').src = img.src;
}

const writeBtn = document.getElementById("writeReviewBtn");
const form = document.getElementById("reviewForm");
const submitBtn = document.getElementById("submitReview");
const commentList = document.querySelector(".comment-list");

// Bấm Write a Review
writeBtn.addEventListener("click", () => {
    form.style.display = form.style.display === "block" ? "none" : "block";
});


//  Bấm Hoàn thành
submitBtn.addEventListener("click", () => {
    const name = document.getElementById("reviewName").value;
    const stars = document.getElementById("reviewStars").value;
    const text = document.getElementById("reviewText").value;

    if (!name || !text) {
        alert("Vui lòng nhập đầy đủ thông tin.");
        return;
    }
});




