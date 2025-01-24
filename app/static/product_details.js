const images = document.querySelectorAll('.image-slider img');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
let currentIndex = 0;

function updateSlider() {
    images.forEach((img, index) => {
        img.classList.toggle('active', index === currentIndex);
    });
}

prevBtn.addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    updateSlider();
});

nextBtn.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % images.length;
    updateSlider();
});