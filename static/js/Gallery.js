class GalleryApp {
    constructor() {
        this.initializeEventListeners();
    }
    initializeEventListeners() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => this.handleSort(e));
        }
        document.querySelectorAll('.artwork-image').forEach(img => {
            img.addEventListener('click', () => this.openModal(img.src));
        });
        const modal = document.getElementById('imageModal');
        if (modal) {
            modal.querySelector('.modal-close').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            window.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        }
    }
    openModal(src) {
        const modal = document.getElementById('imageModal');
        const modalImg = document.getElementById('modalImage');
        modal.style.display = 'block';
        modalImg.src = src;
    }
    handleSort(e) {
        const gallery = document.querySelector('.gallery-grid');
        const artworks = Array.from(gallery.children);
        artworks.sort((a, b) => {
            const dateA = parseFloat(a.dataset.created);
            const dateB = parseFloat(b.dataset.created);
            return e.target.value === 'newest' ? dateB - dateA : dateA - dateB;
        });
        artworks.forEach(artwork => gallery.appendChild(artwork));
    }
}
document.addEventListener('DOMContentLoaded', () => {
    new GalleryApp();
});
