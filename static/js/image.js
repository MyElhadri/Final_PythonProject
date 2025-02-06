document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    if (!uploadForm) return;

    const imageInput = document.getElementById("image");
    const imagePreview = document.getElementById("imagePreview");
    const processedImage = document.getElementById("processedImage");
    const downloadBtn = document.getElementById("downloadBtn");
    const previewResultContainer = document.getElementById("previewResultContainer");

    // Function to display the image preview
    imageInput.addEventListener("change", function () {
        const file = this.files[0];

        if (file) {
            const reader = new FileReader();

            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = "block";
                previewResultContainer.style.display = "flex";
            };

            reader.readAsDataURL(file);
        } else {
            imagePreview.style.display = "none";
            processedImage.style.display = "none";
            previewResultContainer.style.display = "none";
        }
    });

    // Sending the image and displaying the processed result
    uploadForm.addEventListener("submit", (event) => {
        event.preventDefault();

        const formData = new FormData(uploadForm);

        fetch("/apply_filter_ajax", {
            method: "POST",
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("❌ Error: " + data.error);
            } else {
                const processedFilename = data.filename;
                const imageUrl = `/static/images/${processedFilename}?t=${Date.now()}`;

                processedImage.src = imageUrl;
                processedImage.style.display = "block";
                previewResultContainer.style.display = "flex";

                downloadBtn.href = imageUrl;
                downloadBtn.style.display = "block";
            }
        })
        .catch(error => {
            console.error("AJAX Error:", error);
            alert("An error occurred while processing the image.");
        });
    });
});
