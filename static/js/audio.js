document.addEventListener("DOMContentLoaded", function () {
    // 🎼 Génération audio
    const generateBtn = document.getElementById("generate-audio-btn");
    const generatedAudio = document.getElementById("generated-audio");

    generateBtn.addEventListener("click", function () {
        fetch("/generate_audio")
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);
                generatedAudio.src = url;
                generatedAudio.style.display = "block";
                generatedAudio.play();

                // Supprimer un bouton de téléchargement précédent s'il existe
                let existingDownloadBtn = document.getElementById("download-generated-audio");
                if (existingDownloadBtn) {
                    existingDownloadBtn.remove();
                }

                // Ajouter un bouton de téléchargement
                const downloadBtn = document.createElement("a");
                downloadBtn.id = "download-generated-audio";
                downloadBtn.href = url;
                downloadBtn.download = "generated_audio.wav";
                downloadBtn.innerText = "⬇️ Télécharger la Mélodie";
                downloadBtn.classList.add("download-btn");

                generateBtn.parentElement.appendChild(downloadBtn);
            })
            .catch(error => console.error("❌ Erreur JS :", error));
    });

    // 🎚️ Modification audio (changement de vitesse)
    const processForm = document.getElementById("process-audio-form");

    processForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(processForm);

        fetch("/process_audio", {
            method: "POST",
            body: formData
        })
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);

                let existingAudio = document.getElementById("processed-audio");
                if (existingAudio) {
                    existingAudio.remove();
                }

                let existingDownloadBtn = document.getElementById("download-processed-audio");
                if (existingDownloadBtn) {
                    existingDownloadBtn.remove();
                }

                const processedAudio = document.createElement("audio");
                processedAudio.id = "processed-audio";
                processedAudio.controls = true;
                processedAudio.src = url;
                processedAudio.style.display = "block";

                const downloadBtn = document.createElement("a");
                downloadBtn.id = "download-processed-audio";
                downloadBtn.href = url;
                downloadBtn.download = "modified_audio.wav";
                downloadBtn.innerText = "⬇️ Télécharger l'Audio";
                downloadBtn.classList.add("download-btn");

                processForm.appendChild(processedAudio);
                processForm.appendChild(downloadBtn);
                processedAudio.play();
            })
            .catch(error => console.error("❌ Erreur JS :", error));
    });

    // 🔄 Fusion audio
    const mergeForm = document.getElementById("merge-audio-form");

    mergeForm.addEventListener("submit", function (event) {
        event.preventDefault();
        const formData = new FormData(mergeForm);

        fetch("/merge_audio", {
            method: "POST",
            body: formData
        })
            .then(response => response.blob())
            .then(blob => {
                const url = URL.createObjectURL(blob);

                let existingAudio = document.getElementById("merged-audio");
                if (existingAudio) {
                    existingAudio.remove();
                }

                let existingDownloadBtn = document.getElementById("download-merged-audio");
                if (existingDownloadBtn) {
                    existingDownloadBtn.remove();
                }

                const mergedAudio = document.createElement("audio");
                mergedAudio.id = "merged-audio";
                mergedAudio.controls = true;
                mergedAudio.src = url;
                mergedAudio.style.display = "block";

                const downloadBtn = document.createElement("a");
                downloadBtn.id = "download-merged-audio";
                downloadBtn.href = url;
                downloadBtn.download = "merged_audio.wav";
                downloadBtn.innerText = "⬇️ Télécharger l'Audio Fusionné";
                downloadBtn.classList.add("download-btn");

                mergeForm.appendChild(mergedAudio);
                mergeForm.appendChild(downloadBtn);
                mergedAudio.play();
            })
            .catch(error => console.error("❌ Erreur JS :", error));
    });
});
