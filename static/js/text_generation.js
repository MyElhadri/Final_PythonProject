// text_gen.js
document.addEventListener("DOMContentLoaded", () => {
  const textGenForm = document.getElementById("textGenForm");
  if (!textGenForm) return;

  const resultContainer = document.getElementById("generatedResult");

  textGenForm.addEventListener("submit", (event) => {
    event.preventDefault();

    const formData = new FormData(textGenForm);
    fetch("/text_gen_ajax", {
      method: "POST",
      body: formData
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.error) {
        resultContainer.innerHTML = `<p style="color:red;">Erreur: ${data.error}</p>`;
      } else {
        resultContainer.innerHTML = `
          <h4>Résultat :</h4>
          <p>${data.generated_text}</p>
        `;
      }
    })
    .catch((err) => {
      console.error("Erreur AJAX:", err);
      resultContainer.innerHTML = `<p style="color:red;">Une erreur est survenue.</p>`;
    });
  });
});
