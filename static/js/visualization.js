// 📊 visualization.js

document.addEventListener("DOMContentLoaded", function () {
    // Apply a fade-in effect to table rows
    const rows = document.querySelectorAll(".data-table tr");
    rows.forEach((row, index) => {
        row.style.animation = `fadeIn 0.5s ease-in-out ${index * 0.1}s forwards`;
        row.style.opacity = "0";
    });

    // Hover animation effect on the chart image
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

// 🎨 Fade-in animation for tables
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
