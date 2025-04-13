const images = document.querySelectorAll('.image-slider img');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const modelViewerWrapper = document.querySelector('.sketchfab-embed-wrapper');
let currentIndex = 0;

function updateSlider() {
    images.forEach((img, index) => {
        img.classList.toggle('active', index === currentIndex);
    });
}

// Toggle visibility of the 3D model when an image is clicked
images.forEach((image, index) => {
    image.addEventListener('click', () => {
        if (modelViewerWrapper) {
            modelViewerWrapper.style.display = 'block'; // Show the 3D model iframe
            const sketchfabIframe = modelViewerWrapper.querySelector('iframe');
            if (sketchfabIframe) {
                sketchfabIframe.src = sketchfabIframe.src; // Reset the iframe URL to reload the model
            }
        }
    });
});

// Button functionality for the image slider (optional)
nextBtn.addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % images.length;
    updateSlider();
});

prevBtn.addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    updateSlider();
});

// Ensure the 3D model view is hidden by default
if (modelViewerWrapper) {
    modelViewerWrapper.style.display = 'none';
}
