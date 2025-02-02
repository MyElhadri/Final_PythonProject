import io
import random
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.effects import speedup
import numpy as np

# 🔹 Assurez-vous que ffmpeg est bien utilisé
from pydub.utils import which
AudioSegment.converter = which("ffmpeg")


def apply_random_effects(segment):
    """
    Applique aléatoirement quelques effets à un segment audio pour le rendre plus unique.
    Les effets incluent le panning et les fondus en entrée et sortie.
    """
    # Option panning
    if random.random() < 0.5:
        pan_value = random.uniform(-1, 1)
        segment = segment.pan(pan_value)
    # Option fade in
    if random.random() < 0.5:
        fade_in_duration = random.randint(50, 200)  # en millisecondes
        segment = segment.fade_in(fade_in_duration)
    # Option fade out
    if random.random() < 0.5:
        fade_out_duration = random.randint(50, 200)
        segment = segment.fade_out(fade_out_duration)
    return segment


def generate_random_melody():
    """
    Génère une mélodie aléatoire d'une durée totale de 15 secondes.
    Chaque note a une durée aléatoire et se voit appliquer des effets sonores aléatoires
    pour que chaque mélodie soit distincte.
    """
    notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # Notes de Do à Do
    total_duration = 15000  # 15 secondes
    melody = AudioSegment.silent(duration=0)

    try:
        while len(melody) < total_duration:
            freq = random.choice(notes)
            # Durée aléatoire pour la note entre 300ms et 700ms
            duration_per_note = random.randint(300, 700)
            # Générer la note avec la fréquence choisie
            tone = Sine(freq).to_audio_segment(duration=duration_per_note)
            # Appliquer un gain aléatoire entre -10 et -2 dB
            gain = random.uniform(-10, -2)
            tone = tone.apply_gain(gain)
            # Appliquer des effets aléatoires (panning, fade in/out)
            tone = apply_random_effects(tone)
            melody += tone

        # S'assurer que la mélodie dure exactement 15 secondes
        melody = melody[:total_duration]

        buffer = io.BytesIO()
        melody.export(buffer, format="wav")
        buffer.seek(0)
        return buffer
    except Exception as e:
        print("❌ Erreur lors de la génération de la mélodie :", e)
        raise


def get_file_format(audio_file, default="wav"):
    """
    Détermine le format du fichier audio à partir de son nom.
    Accepte .wav et .mp3 ; sinon, retourne la valeur par défaut.
    """
    try:
        filename = audio_file.filename
        ext = filename.rsplit('.', 1)[-1].lower()
        if ext in ["wav", "mp3"]:
            return ext
        else:
            return default
    except Exception:
        return default


def change_audio_speed(audio_file, speed):
    """
    Modifie la vitesse d'un fichier audio sans changer le pitch.
    Accepte les fichiers .wav et .mp3 et fonctionne avec des audios de longue durée.
    """
    try:
        file_format = get_file_format(audio_file, default="wav")
        # Réinitialiser le curseur du fichier
        audio_file.seek(0)
        segment = AudioSegment.from_file(audio_file, format=file_format)

        if speed > 1.0:
            # Accélération via speedup()
            segment = speedup(segment, playback_speed=speed)
        elif speed < 1.0:
            # Ralentissement : interpolation des données audio
            samples = np.array(segment.get_array_of_samples())
            new_length = int(len(samples) / speed)
            slowed_samples = np.interp(
                np.linspace(0, len(samples), new_length),
                np.arange(len(samples)),
                samples
            ).astype(samples.dtype)
            segment = AudioSegment(
                slowed_samples.tobytes(),
                frame_rate=segment.frame_rate,
                sample_width=segment.sample_width,
                channels=segment.channels
            )

        buffer = io.BytesIO()
        segment.export(buffer, format=file_format)
        buffer.seek(0)
        return buffer
    except Exception as e:
        print("❌ Erreur lors de la modification de la vitesse :", e)
        raise


def merge_audio_files(audio_file1, audio_file2):
    """
    Fusionne deux fichiers audio en équilibrant les volumes.
    Accepte les fichiers .wav et .mp3.
    """
    try:
        format1 = get_file_format(audio_file1, default="wav")
        format2 = get_file_format(audio_file2, default="wav")
        # Réinitialiser le curseur des fichiers
        audio_file1.seek(0)
        audio_file2.seek(0)
        seg1 = AudioSegment.from_file(audio_file1, format=format1)
        seg2 = AudioSegment.from_file(audio_file2, format=format2)

        # Harmonisation des fréquences d'échantillonnage
        if seg1.frame_rate != seg2.frame_rate:
            seg2 = seg2.set_frame_rate(seg1.frame_rate)

        # Ajustement des volumes pour éviter la saturation
        seg1 = seg1 - 3
        seg2 = seg2 - 3

        # Fusion par superposition (overlay)
        merged_segment = seg1.overlay(seg2)

        buffer = io.BytesIO()
        # Exporter toujours en WAV (format de sortie choisi)
        merged_segment.export(buffer, format="wav")
        buffer.seek(0)
        return buffer
    except Exception as e:
        print("❌ Erreur lors de la fusion des audios :", e)
        raise

