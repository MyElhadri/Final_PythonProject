document.addEventListener("DOMContentLoaded", () => {
    // 1) GESTION DE L'AFFICHAGE DES SECTIONS
    const sections = document.querySelectorAll(".audio-section");

    function showSection(sectionClass) {
        sections.forEach(s => s.style.display = "none");
        const target = document.querySelector("." + sectionClass);
        if (target) target.style.display = "block";
    }

    document.getElementById("btn-generate")
        .addEventListener("click", () => showSection("generate"));
    document.getElementById("btn-process")
        .addEventListener("click", () => showSection("process"));
    document.getElementById("btn-merge")
        .addEventListener("click", () => showSection("merge"));
    document.getElementById("btn-filter")
        .addEventListener("click", () => showSection("filter"));

    // 2) INSTALLER L'APERCU IMMEDIAT DES FICHIERS
    function setupAudioPreview(labelId, inputId, fileNameId, audioId) {
        const label          = document.getElementById(labelId);
        const fileInput      = document.getElementById(inputId);
        const fileNameDisplay= document.getElementById(fileNameId);
        const audioPreview   = document.getElementById(audioId);

        // Quand on clique sur le label, on réinitialise et on ouvre le sélecteur
        label.addEventListener("click", () => {
            fileInput.value = "";   // reset pour forcer l'événement "change" même si le même fichier est choisi
            fileInput.click();
        });

        // Quand on change de fichier, on affiche un aperçu
        fileInput.addEventListener("change", () => {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const fileURL = URL.createObjectURL(file);

                // Mettre à jour la prévisualisation
                audioPreview.src = fileURL;
                audioPreview.style.display = "block";
                fileNameDisplay.textContent = `✔️ ${file.name}`;
                label.textContent = "✅ Fichier sélectionné";
            }
        });
    }

    // Appliquer la fonction sur nos 4 inputs
    setupAudioPreview("label-file1", "file1", "file-name1", "preview-audio1");
    setupAudioPreview("label-file2", "file2", "file-name2", "preview-audio2");
    setupAudioPreview("label-file3", "file3", "file-name3", "preview-audio3");
    setupAudioPreview("label-file-filter", "file-filter", "file-name4", "preview-audio4");

    // 3) GÉNÉRATION D'UNE MÉLODIE
    const generateBtn    = document.getElementById("generate-audio-btn");
    const generatedAudio = document.getElementById("generated-audio");
    if (generateBtn && generatedAudio) {
        generateBtn.addEventListener("click", () => {
            fetch("/generate_audio")
                .then(response => response.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);
                    generatedAudio.src = url;
                    generatedAudio.style.display = "block";
                    generatedAudio.play();

                    // Bouton de téléchargement
                    let existingDownloadBtn = document.getElementById("download-generated-audio");
                    if (existingDownloadBtn) existingDownloadBtn.remove();

                    const downloadBtn = document.createElement("a");
                    downloadBtn.id = "download-generated-audio";
                    downloadBtn.href = url;
                    downloadBtn.download = "generated_audio.wav";
                    downloadBtn.innerText = "⬇️ Télécharger la Mélodie";
                    downloadBtn.classList.add("download-btn");
                    generateBtn.parentElement.appendChild(downloadBtn);
                })
                .catch(err => console.error("❌ Erreur JS (génération) :", err));
        });
    }

    // 4) MODIFICATION AUDIO (changement de vitesse)
    const processForm = document.getElementById("process-audio-form");
    if (processForm) {
        processForm.addEventListener("submit", event => {
            event.preventDefault();
            const formData = new FormData(processForm);

            fetch("/process_audio", {
                method: "POST",
                body: formData
            })
                .then(r => r.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);

                    let existingAudio = document.getElementById("processed-audio");
                    if (existingAudio) existingAudio.remove();

                    let existingDownloadBtn = document.getElementById("download-processed-audio");
                    if (existingDownloadBtn) existingDownloadBtn.remove();

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
                .catch(err => console.error("❌ Erreur JS (process) :", err));
        });
    }

    // 5) FUSION AUDIO
    const mergeForm = document.getElementById("merge-audio-form");
    if (mergeForm) {
        mergeForm.addEventListener("submit", event => {
            event.preventDefault();
            const formData = new FormData(mergeForm);

            fetch("/merge_audio", {
                method: "POST",
                body: formData
            })
                .then(r => r.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);

                    let existingAudio = document.getElementById("merged-audio");
                    if (existingAudio) existingAudio.remove();

                    let existingDownloadBtn = document.getElementById("download-merged-audio");
                    if (existingDownloadBtn) existingDownloadBtn.remove();

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
                .catch(err => console.error("❌ Erreur JS (merge) :", err));
        });
    }

    // 6) APPLIQUER UN FILTRE AUDIO
    const filterForm = document.getElementById("filter-audio-form");
    if (filterForm) {
        filterForm.addEventListener("submit", event => {
            event.preventDefault();
            const formData = new FormData(filterForm);

            fetch("/apply_audio_filter", {
                method: "POST",
                body: formData
            })
                .then(r => r.blob())
                .then(blob => {
                    const url = URL.createObjectURL(blob);

                    let existingAudio = document.getElementById("filtered-audio");
                    if (existingAudio) existingAudio.remove();

                    const filteredAudio = document.createElement("audio");
                    filteredAudio.id = "filtered-audio";
                    filteredAudio.controls = true;
                    filteredAudio.src = url;
                    filteredAudio.style.display = "block";

                    filterForm.appendChild(filteredAudio);
                    filteredAudio.play();
                })
                .catch(err => console.error("❌ Erreur JS (filtre) :", err));
        });
    }
});
