// 📊 visualization.js

document.addEventListener("DOMContentLoaded", function () {

    // Appliquer un effet d'apparition aux lignes du tableau
    const rows = document.querySelectorAll(".data-table tr");
    rows.forEach((row, index) => {
        row.style.animation = `fadeIn 0.5s ease-in-out ${index * 0.1}s forwards`;
        row.style.opacity = "0";
    });

    // Effet d'animation sur l'image du graphique
    const chartImage = document.querySelector(".chart-container img");
    if (chartImage) {
        chartImage.addEventListener("mouseenter", function () {
            this.style.transform = "scale(1.1)";
            this.style.filter = "hue-rotate(30deg)";
        });

        chartImage.addEventListener("mouseleave", function () {
            this.style.transform = "scale(1)";
            this.style.filter = "hue-rotate(0deg)";
        });
    }
});

// 🎨 Animation d'apparition des tableaux
const style = document.createElement("style");
style.innerHTML = `
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}`;
document.head.appendChild(style);
