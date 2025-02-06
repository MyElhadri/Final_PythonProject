// 🎨 art.js - Enhancing User Experience

// Function to show/hide the color picker with animation
function toggleColorPicker() {
    var colorScheme = document.getElementById("color_scheme");
    var colorPicker = document.getElementById("custom_color");

    if (colorScheme.value === "custom") {
        colorPicker.style.display = "block";
        colorPicker.style.opacity = "0";
        setTimeout(() => { colorPicker.style.opacity = "1"; }, 200); // Smooth animation
        colorPicker.required = true;
    } else {
        colorPicker.style.opacity = "0";
        setTimeout(() => { colorPicker.style.display = "none"; }, 300); // Smooth disappearance
        colorPicker.required = false;
    }
}

// Function to handle form submission without confirmation
function handleFormSubmit(event) {
    var colorScheme = document.getElementById("color_scheme").value;
    var colorPicker = document.getElementById("custom_color");

    // Check if a custom color is selected but not chosen
    if (colorScheme === "custom" && !colorPicker.value) {
        alert("🎨 Please select a custom color!");
        event.preventDefault(); // Prevent form submission
    }
}

// Execute on load to set the initial state and bind events
document.addEventListener("DOMContentLoaded", function () {
    toggleColorPicker(); // Apply correct visibility on startup

    // Event listener for the color palette selector change
    document.getElementById("color_scheme").addEventListener("change", toggleColorPicker);

    // Remove confirmation before generating
    document.querySelector(".art-form").addEventListener("submit", handleFormSubmit);
});
