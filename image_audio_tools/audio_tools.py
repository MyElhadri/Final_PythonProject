import io
import time
import random
import numpy as np
from pydub import AudioSegment
from pydub.generators import Sine
from pydub.effects import speedup, normalize
from pydub.utils import which

# Configuration de pydub pour trouver ffmpeg / ffprobe
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffprobe   = which("ffprobe")

print("ffmpeg used by pydub:", AudioSegment.converter)
print("ffprobe used by pydub:", AudioSegment.ffprobe)

##################################################
# 1) Paramètres généraux pour générer la mélodie
##################################################
TOTAL_DURATION_MS = 15000  # 15 secondes
FADE_IN_MS = 300
FADE_OUT_MS = 600

# Durées possibles (en ms) pour chaque mesure
MEASURE_DURATION_CHOICES = [1800, 2000, 2200]
MIN_MEASURES = 6
MAX_MEASURES = 8

# Profils d'instruments d'accompagnement
INSTRUMENT_PROFILES_ACCOMP = {
    "piano": [(1, 0), (2, -6), (3, -9)],
    "acoustic_guitar": [(1, 0), (2, -4), (3, -8), (4, -12)],
    "harp": [(1, 0), (2, -8)],
    "organ": [(1, 0), (2, -4), (3, -8), (4, -12)],
    "electric_piano": [(1, 0), (2, -4), (3, -8)],
    "mandolin": [(1, 0), (2, -4), (3, -8)],
    "banjo": [(1, 0), (2, -4), (3, -8)]
}

# Profils d'instruments solistes
INSTRUMENT_PROFILES_SOLO = {
    "flute": [(1, 0), (2, -10)],
    "violin": [(1, 0), (2, -3), (3, -7)],
    "saxophone": [(1, 0), (2, -7), (3, -12)],
    "trumpet": [(1, 0), (2, -5), (3, -10)],
    "clarinet": [(1, 0), (3, -7)],
    "duduk": [(1, 0), (2, -8)],
    "electric_guitar_solo": [(1, 0), (2, -3), (3, -7), (4, -10)],
    "erhu": [(1, 0), (2, -5), (3, -10)]
}

def get_instrument_profile(name):
    if name in INSTRUMENT_PROFILES_ACCOMP:
        return INSTRUMENT_PROFILES_ACCOMP[name]
    if name in INSTRUMENT_PROFILES_SOLO:
        return INSTRUMENT_PROFILES_SOLO[name]
    return [(1, 0)]  # par défaut si introuvable

##################################################
# 2) Fonctions d'effets aléatoires
##################################################
def apply_random_effects(segment):
    # panning, fade in/out
    if random.random() < 0.5:
        segment = segment.pan(random.uniform(-0.8, 0.8))
    if random.random() < 0.5:
        segment = segment.fade_in(random.randint(50, 200))
    if random.random() < 0.5:
        segment = segment.fade_out(random.randint(50, 200))
    return segment

def apply_reverb(segment):
    # Reverb simple
    delay = random.randint(80, 300)
    attenuation = random.uniform(5, 12)
    rev = AudioSegment.silent(duration=delay) + segment - attenuation
    return segment.overlay(rev)

def apply_extra_effects(segment):
    # echo
    if random.random() < 0.7:
        delay = random.randint(100, 400)
        att = random.uniform(4, 10)
        echo = AudioSegment.silent(duration=delay) + segment - att
        segment = segment.overlay(echo)

    # reverb
    if random.random() < 0.4:
        segment = apply_reverb(segment)

    # low-pass
    if random.random() < 0.5:
        cutoff = random.randint(300, 1500)
        segment = segment.low_pass_filter(cutoff)

    # high-pass
    if random.random() < 0.4:
        cutoff2 = random.randint(1800, 5000)
        segment = segment.high_pass_filter(cutoff2)
    return segment

def apply_all_effects(segment):
    segment = apply_random_effects(segment)
    segment = apply_extra_effects(segment)
    return segment

##################################################
# 3) Génération de notes / assemblage
##################################################
def generate_instrument_note(instrument_name, freq, duration_ms):
    profile = get_instrument_profile(instrument_name)
    base = None
    for harmonic, gain_db in profile:
        tone = Sine(freq * harmonic).to_audio_segment(duration=duration_ms)
        tone = tone.apply_gain(gain_db)
        if base is None:
            base = tone
        else:
            base = base.overlay(tone)
    return base

def append_with_crossfade(existing, segment, crossfade_duration):
    if len(existing) == 0:
        return segment
    xfade = min(crossfade_duration, len(segment) - 1)
    return existing.append(segment, crossfade=xfade)

##################################################
# 4) Gammes, accords, progressions
##################################################
CHROMATIC_BASES = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99,
                   392.00, 415.30, 440.00, 466.16, 493.88]

MAJOR_STEPS = [0, 2, 4, 5, 7, 9, 11]
MINOR_STEPS = [0, 2, 3, 5, 7, 9, 10]

PROGRESSIONS_MAJOR = [
    ["I", "V", "vi", "IV"],
    ["ii", "V", "I", "I"],
    ["I", "IV", "V", "I"],
    ["I", "V", "I", "V"],
    ["vi", "IV", "I", "V"],
    ["ii", "vi", "V", "I"]
]
PROGRESSIONS_MINOR = [
    ["i", "VII", "VI", "v"],
    ["i", "iv", "VII", "III"],
    ["i", "VI", "III", "VII"],
    ["i", "III", "VII", "i"]
]

CHORD_DEGREES_MAJOR = {
    "I":  [0, 2, 4],
    "V":  [4, 6, 1],
    "vi": [5, 0, 2],
    "IV": [3, 5, 0],
    "ii": [1, 3, 5],
    "iii":[2, 4, 6],
    "vii":[6, 1, 3]
}
CHORD_DEGREES_MINOR = {
    "i":  [0, 2, 4],
    "III":[2, 4, 6],
    "VII":[6, 1, 3],
    "v":  [4, 6, 1],
    "iv": [3, 5, 0],
    "VI": [5, 0, 2]
}

##################################################
# 5) Construction segments (accompagnement + mélodie + percu)
##################################################
def build_chord_segment(accomp_instrument, chord_freqs, measure_dur):
    seg = AudioSegment.silent(duration=0)
    random.shuffle(chord_freqs)
    step = measure_dur // len(chord_freqs)
    for f in chord_freqs:
        n = generate_instrument_note(accomp_instrument, f, step)
        n = n.apply_gain(random.uniform(-10, -2))
        n = apply_all_effects(n)
        seg = append_with_crossfade(seg, n, crossfade_duration=80)
    return seg[:measure_dur]

def build_melody_segment(solo_instrument, scale_freqs, measure_dur, current_note_freq):
    seg = AudioSegment.silent(duration=0)
    num_notes = random.randint(2, 4)
    step = measure_dur // num_notes
    freq = current_note_freq

    for _ in range(num_notes):
        diffs = [abs(sf - freq) for sf in scale_freqs]
        i_closest = diffs.index(min(diffs))
        i_new = max(0, min(i_closest + random.choice([-1, 0, 1]), len(scale_freqs)-1))
        freq_new = scale_freqs[i_new]

        n = generate_instrument_note(solo_instrument, freq_new, step)
        n = n.apply_gain(random.uniform(-10, -2))
        n = apply_all_effects(n)

        seg = append_with_crossfade(seg, n, crossfade_duration=60)
        freq = freq_new

    return seg[:measure_dur], freq

def build_simple_percussion(measure_dur):
    seg = AudioSegment.silent(duration=0)
    quarter = measure_dur // 4

    def gen_kick(dur):
        tone = Sine(60).to_audio_segment(duration=dur).apply_gain(-5)
        tone = tone.high_pass_filter(50)
        tone = tone.low_pass_filter(100)
        tone = apply_random_effects(tone)
        return tone

    def gen_snare(dur):
        tone = Sine(200).to_audio_segment(duration=dur).apply_gain(0)
        for _ in range(3):
            f = 200 * random.uniform(0.9, 1.1)
            partial = Sine(f).to_audio_segment(duration=dur).apply_gain(-10)
            tone = tone.overlay(partial)
        tone = tone.high_pass_filter(150)
        tone = tone.fade_out(20)
        return tone

    pattern = [gen_kick(quarter), gen_snare(quarter), gen_kick(quarter), gen_snare(quarter)]
    for p in pattern:
        seg = append_with_crossfade(seg, p, crossfade_duration=30)
    return seg[:measure_dur]

##################################################
# 6) Fonction principale: generate_random_melody
##################################################
def generate_random_melody():
    """
    Génére ~15s de musique variée :
      - Tonalité aléatoire (majeure ou mineure)
      - Progression d'accords
      - Instruments aléatoires
      - Percussions
      - Effets, crossfade etc.
    """
    random.seed(time.time())

    base_freq = random.choice(CHROMATIC_BASES)
    is_major = (random.random() < 0.6)
    scale_steps = MAJOR_STEPS if is_major else MINOR_STEPS

    # Construire la gamme diatonique
    scale_freqs = []
    for deg in scale_steps:
        freq_ = base_freq * (2.0 ** (deg / 12.0))
        scale_freqs.append(freq_)

    if is_major:
        progression_label = random.choice(PROGRESSIONS_MAJOR)
        chord_degrees_map = CHORD_DEGREES_MAJOR
    else:
        progression_label = random.choice(PROGRESSIONS_MINOR)
        chord_degrees_map = CHORD_DEGREES_MINOR

    nb_measures = random.randint(MIN_MEASURES, MAX_MEASURES)

    accomp_instrument = random.choice(list(INSTRUMENT_PROFILES_ACCOMP.keys()))
    solo_instrument   = random.choice(list(INSTRUMENT_PROFILES_SOLO.keys()))

    music = AudioSegment.silent(duration=0)
    current_melody_freq = scale_freqs[random.randint(0, len(scale_freqs)-1)]
    chord_index = 0

    for measure_i in range(nb_measures):
        measure_dur = random.choice(MEASURE_DURATION_CHOICES)

        chord_symb = progression_label[chord_index % len(progression_label)]
        chord_degs = chord_degrees_map.get(chord_symb, [0,2,4])

        chord_freqs = []
        for d in chord_degs:
            semitones = scale_steps[d]
            freq = base_freq * (2.0 ** (semitones / 12.0))
            chord_freqs.append(freq)

        if random.random() < 0.2:
            accomp_instrument = random.choice(list(INSTRUMENT_PROFILES_ACCOMP.keys()))

        chord_seg = build_chord_segment(accomp_instrument, chord_freqs, measure_dur)

        if random.random() < 0.2:
            solo_instrument = random.choice(list(INSTRUMENT_PROFILES_SOLO.keys()))

        melody_seg, current_melody_freq = build_melody_segment(
            solo_instrument, scale_freqs, measure_dur, current_melody_freq
        )

        measure_seg = chord_seg.overlay(melody_seg)

        if random.random() < 0.5:  # Ajouter percussions ?
            drums = build_simple_percussion(measure_dur)
            measure_seg = measure_seg.overlay(drums - 5)

        music = append_with_crossfade(music, measure_seg, crossfade_duration=100)
        chord_index += 1

    music = music[:TOTAL_DURATION_MS]
    music = music.fade_in(FADE_IN_MS).fade_out(FADE_OUT_MS)

    buf = io.BytesIO()
    music.export(buf, format="wav")
    buf.seek(0)
    return buf

##################################################
# 7) Fonctions utiles : change_audio_speed, merge_audio_files
##################################################
def change_audio_speed(audio_file, speed):
    """
    Modifie la vitesse d'un fichier audio (wav/mp3) sans changer le pitch.
    Gère speed > 1.0 (accélération) et speed < 1.0 (ralentissement),
    en s'assurant que la taille finale soit multiple du nombre de canaux.
    """
    try:
        file_format = 'wav'
        fname = getattr(audio_file,'filename', None)
        if fname and '.' in fname:
            ext = fname.rsplit('.',1)[-1].lower()
            if ext in ['wav','mp3']:
                file_format = ext

        audio_file.seek(0)
        seg = AudioSegment.from_file(audio_file, format=file_format)

        if speed > 1.0:
            # Cas d'accélération : on peut utiliser directement speedup() de pydub
            seg = speedup(seg, playback_speed=speed)
        elif speed < 1.0:
            # Cas de ralentissement : on interpole manuellement
            channels = seg.channels
            samples = np.array(seg.get_array_of_samples())
            # Calculer la nouvelle taille (plus grande pour un ralentissement)
            new_len = int(len(samples) / speed)

            # Assurer qu'on ait un multiple du nombre de canaux
            # (pour éviter l'erreur "data length must be multiple of sample_width*channels")
            remainder = new_len % channels
            if remainder != 0:
                new_len -= remainder

            if new_len < channels:
                # En cas d'arrondi extrême, on force au minimum
                new_len = channels

            # Interpolation
            slowed = np.interp(
                np.linspace(0, len(samples), new_len),
                np.arange(len(samples)),
                samples
            ).astype(samples.dtype)

            # Vérifier une dernière fois la divisibilité
            remainder2 = len(slowed) % channels
            if remainder2 != 0:
                slowed = slowed[:(len(slowed) - remainder2)]

            seg = AudioSegment(
                slowed.tobytes(),
                frame_rate=seg.frame_rate,
                sample_width=seg.sample_width,
                channels=channels
            )

        # else: speed == 1.0 => on ne fait rien, c'est inchangé

        out = io.BytesIO()
        seg.export(out, format="wav")
        out.seek(0)
        return out
    except Exception as e:
        raise e

def merge_audio_files(file1, file2):
    """
    Fusionne deux fichiers audio (wav/mp3) en overlay
    en baissant chaque piste de 3dB.
    """
    try:
        def get_fmt(f):
            nm = getattr(f,'filename',None)
            if nm and '.' in nm:
                ex = nm.rsplit('.',1)[-1].lower()
                if ex in ['wav','mp3']:
                    return ex
            return 'wav'

        fmt1 = get_fmt(file1)
        fmt2 = get_fmt(file2)

        file1.seek(0)
        seg1 = AudioSegment.from_file(file1, format=fmt1)
        file2.seek(0)
        seg2 = AudioSegment.from_file(file2, format=fmt2)

        if seg1.frame_rate != seg2.frame_rate:
            seg2 = seg2.set_frame_rate(seg1.frame_rate)

        seg1 = seg1 - 3
        seg2 = seg2 - 3

        merged = seg1.overlay(seg2)
        buf = io.BytesIO()
        merged.export(buf, format="wav")
        buf.seek(0)
        return buf
    except Exception as e:
        raise e

##################################################
# 8) Application de 10 filtres + (11) Autotune
##################################################
def apply_filter_to_audio(audio_file, filter_type):
    """
    Applique 11 filtres possibles :
      1=Low-pass doux, 2=High-pass,
      3=Echo, 4=Reverb,
      5=Overdrive léger, 6=Distorsion,
      7=Chorus, 8=Phaser,
      9=Robotize (pitch shift),
      10=Compresseur,
      11=Autotune (simplifié).
    """
    audio_file.seek(0)
    file_format = 'wav'
    fname = getattr(audio_file,'filename', None)
    if fname and '.' in fname:
        ext = fname.rsplit('.',1)[-1].lower()
        if ext in ['wav','mp3']:
            file_format = ext

    seg = AudioSegment.from_file(audio_file, format=file_format)

    ftype = str(filter_type)
    if ftype == "1":
        seg = seg.low_pass_filter(800)
    elif ftype == "2":
        seg = seg.high_pass_filter(1200)
    elif ftype == "3":
        seg = apply_echo(seg)
    elif ftype == "4":
        seg = apply_reverb_simple(seg)
    elif ftype == "5":
        seg = apply_overdrive(seg, drive_db=10)
    elif ftype == "6":
        seg = apply_overdrive(seg, drive_db=18)
    elif ftype == "7":
        seg = apply_chorus(seg)
    elif ftype == "8":
        seg = apply_phaser(seg)
    elif ftype == "9":
        seg = apply_pitch_shift(seg, semitones=-6)
    elif ftype == "10":
        seg = apply_compressor(seg)
    elif ftype == "11":
        seg = apply_autotine(seg)  # Autotune simplifié

    out_buf = io.BytesIO()
    seg.export(out_buf, format="wav")
    out_buf.seek(0)
    return out_buf

def apply_echo(segment, delay_ms=200, attenuation_db=6):
    echo_seg = AudioSegment.silent(duration=delay_ms) + segment - attenuation_db
    return segment.overlay(echo_seg)

def apply_reverb_simple(segment):
    delay = random.randint(100, 400)
    att = random.uniform(6,12)
    rev = AudioSegment.silent(duration=delay) + segment - att
    return segment.overlay(rev)

def apply_overdrive(segment, drive_db=10):
    seg_loud = segment.apply_gain(drive_db)
    seg_loud = seg_loud.high_pass_filter(50)
    return segment.overlay(seg_loud)

def apply_chorus(segment):
    echo1 = AudioSegment.silent(duration=30) + segment - 6
    echo2 = AudioSegment.silent(duration=60) + segment - 6
    combined = segment.overlay(echo1).overlay(echo2)
    return combined.fade_out(50)

def apply_phaser(segment):
    out = segment
    for ms_delay in [15, 30, 45, 60]:
        phase_seg = AudioSegment.silent(duration=ms_delay) + segment - random.uniform(3,8)
        out = out.overlay(phase_seg)
    return out.fade_out(50)

def apply_pitch_shift(segment, semitones=-6):
    samples = np.array(segment.get_array_of_samples())
    ratio = 2 ** (semitones / 12.0)
    new_len = int(len(samples) / ratio)
    pitched = np.interp(
        np.linspace(0, len(samples), new_len),
        np.arange(len(samples)),
        samples
    ).astype(samples.dtype)

    seg2 = AudioSegment(
        pitched.tobytes(),
        frame_rate=int(segment.frame_rate * ratio),
        sample_width=segment.sample_width,
        channels=segment.channels
    )
    seg2 = seg2.set_frame_rate(segment.frame_rate)
    return seg2

def apply_compressor(segment):
    seg2 = normalize(segment)
    peak_level = seg2.max_dBFS
    if peak_level > -2.0:
        reduction = peak_level - (-2.0)
        seg2 = seg2.apply_gain(-reduction)
    return seg2

##################################################
# 9) Autotune (simplifié) : Filtre 11
##################################################
def apply_autotine(segment, chunk_ms=50):
    """
    Applique un 'autotune' basique :
      - Découpe l'audio en mini-chunks (50 ms)
      - Détecte la fréquence fondamentale
      - Snap à la note la + proche (do majeur)
      - Pitch shift
    """
    import numpy as np

    note_freqs = [
        261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99,
        392.00, 415.30, 440.00, 466.16, 493.88, 523.25
    ]

    sr = segment.frame_rate
    channels = segment.channels
    raw_data = segment.get_array_of_samples()
    samples = np.array(raw_data, dtype=np.int16)

    # Mono
    if channels > 1:
        samples = samples.reshape((-1, channels))
        mono = np.mean(samples, axis=1).astype(np.int16)
    else:
        mono = samples

    chunk_size = int(sr * chunk_ms / 1000.0)
    total_samples = len(mono)
    output = np.zeros_like(mono)

    pos = 0
    out_pos = 0
    while pos < total_samples:
        chunk = mono[pos:pos+chunk_size]
        if len(chunk) == 0:
            break

        freq_est = detect_pitch_autocorr(chunk, sr)
        if freq_est is not None:
            nearest = min(note_freqs, key=lambda x: abs(x - freq_est))
            ratio = nearest / freq_est
        else:
            ratio = 1.0

        pitched_chunk = pitch_shift_array(chunk, ratio)
        if out_pos + len(pitched_chunk) > len(output):
            pitched_chunk = pitched_chunk[:(len(output) - out_pos)]

        output[out_pos: out_pos + len(pitched_chunk)] = pitched_chunk
        out_pos += len(pitched_chunk)
        pos += len(chunk)

    if channels > 1:
        # Re-dupliquer sur 2 canaux
        out_stereo = np.repeat(output[:, np.newaxis], channels, axis=1).flatten().astype(np.int16)
        data_final = out_stereo
    else:
        data_final = output

    seg2 = AudioSegment(
        data_final.tobytes(),
        frame_rate=sr,
        sample_width=segment.sample_width,
        channels=channels
    )

    return seg2

def detect_pitch_autocorr(chunk, sr):
    """
    Détermine la fréquence dominante par autocorrélation.
    chunk = np.array int16
    """
    import numpy as np
    if len(chunk) < 2:
        return None

    chunk_float = chunk.astype(np.float32)
    corr = np.correlate(chunk_float, chunk_float, mode='full')
    corr = corr[len(corr)//2:]
    if len(corr) < 2:
        return None

    peak_index = np.argmax(corr[1:]) + 1
    peak_value = corr[peak_index]
    if peak_value < 1e-5:
        return None

    lag = peak_index
    freq_est = sr / lag
    if freq_est < 50 or freq_est > 2000:
        return None
    return freq_est

def pitch_shift_array(chunk, ratio):
    """
    Pitch shift sur un array mono, ratio > 1 => fréquence monte => chunk raccourcit.
    """
    import numpy as np
    length_in = len(chunk)
    length_out = int(length_in / ratio)
    if length_out < 1:
        return np.array([], dtype=chunk.dtype)

    out_array = np.interp(
        np.linspace(0, length_in, length_out),
        np.arange(length_in),
        chunk
    ).astype(chunk.dtype)
    return out_array
