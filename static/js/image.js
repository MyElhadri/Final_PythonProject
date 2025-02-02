document.addEventListener("DOMContentLoaded", () => {
  const uploadForm = document.getElementById("uploadForm");
  if (!uploadForm) return;

  const resultContainer = document.getElementById("resultContainer");

  uploadForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const formData = new FormData(uploadForm);

    // On suppose que votre route est /apply_filter_ajax
    fetch("/apply_filter_ajax", {
      method: "POST",
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        alert("Erreur : " + data.error);
      } else {
        const processedFilename = data.filename;
        // On insère l'image directement dans la page
        const imgHtml = `
          <h4>Résultat :</h4>
          <img src="/static/images/${processedFilename}?t=${Date.now()}" alt="Image traitée">
        `;
        resultContainer.innerHTML = imgHtml;
      }
    })
    .catch(error => {
      console.error("Erreur AJAX:", error);
      alert("Une erreur est survenue lors du traitement de l'image.");
    });
  });
});
