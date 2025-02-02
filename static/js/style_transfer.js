document.addEventListener("DOMContentLoaded", function() {
    // Get references to file inputs, preview elements, and the new custom buttons.
    const contentInput = document.getElementById('content_image');
    const styleInput = document.getElementById('style_image');
    const contentPreview = document.getElementById('contentPreview');
    const stylePreview = document.getElementById('stylePreview');
    const contentButton = document.getElementById('contentButton');
    const styleButton = document.getElementById('styleButton');
    const form = document.getElementById('styleTransferForm');
    const loadingIndicator = document.getElementById('loading');

    // Function to read a file and display it as a preview.
    function readURL(input, previewElement) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewElement.src = e.target.result;
                previewElement.style.display = 'block';
            }
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Bind click events to the new buttons to trigger the hidden file inputs.
    contentButton.addEventListener('click', function() {
        contentInput.click();
    });
    styleButton.addEventListener('click', function() {
        styleInput.click();
    });

    // Set up change listeners for the file inputs.
    contentInput.addEventListener('change', function() {
        readURL(this, contentPreview);
    });

    styleInput.addEventListener('change', function() {
        readURL(this, stylePreview);
    });

    // When the form is submitted, show the loading indicator.
    form.addEventListener('submit', function(e) {
        loadingIndicator.style.display = 'block';
    });
});
