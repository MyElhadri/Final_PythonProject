// 🎨 art.js - Amélioration de l'expérience utilisateur

// Fonction pour afficher/masquer la pipette avec animation
function toggleColorPicker() {
    var colorScheme = document.getElementById("color_scheme");
    var colorPicker = document.getElementById("custom_color");

    if (colorScheme.value === "custom") {
        colorPicker.style.display = "block";
        colorPicker.style.opacity = "0";
        setTimeout(() => { colorPicker.style.opacity = "1"; }, 200); // Animation douce
        colorPicker.required = true;
    } else {
        colorPicker.style.opacity = "0";
        setTimeout(() => { colorPicker.style.display = "none"; }, 300); // Disparition douce
        colorPicker.required = false;
    }
}

// Fonction pour gérer la soumission du formulaire sans confirmation
function handleFormSubmit(event) {
    var colorScheme = document.getElementById("color_scheme").value;
    var colorPicker = document.getElementById("custom_color");

    // Vérifier si une couleur personnalisée est choisie mais non sélectionnée
    if (colorScheme === "custom" && !colorPicker.value) {
        alert("🎨 Veuillez choisir une couleur personnalisée !");
        event.preventDefault(); // Empêcher la soumission
    }
}

// Exécuter au chargement pour définir l'état initial et lier les événements
document.addEventListener("DOMContentLoaded", function () {
    toggleColorPicker(); // Appliquer la bonne visibilité au démarrage

    // Écouteur d'événement pour le changement du sélecteur de palette de couleurs
    document.getElementById("color_scheme").addEventListener("change", toggleColorPicker);

    // Suppression de la confirmation avant génération
    document.querySelector(".art-form").addEventListener("submit", handleFormSubmit);
});
