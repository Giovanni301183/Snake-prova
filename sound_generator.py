"""
sound_generator.py
Generatore procedurale di effetti sonori WAV a 16-bit PCM (44.1 kHz).
Crea file audio autentici in stile arcade/retro senza dipendenze esterne.
"""

import os
import math
import wave
import struct

SAMPLE_RATE = 44100

def write_wav(file_path: str, samples: list[float], sample_rate: int = SAMPLE_RATE):
    """Scrive una lista di campioni normalizzati [-1.0, 1.0] su file WAV."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with wave.open(file_path, 'w') as wav_file:
        wav_file.setnchannels(1)        # Mono
        wav_file.setsampwidth(2)        # 16-bit
        wav_file.setframerate(sample_rate)
        
        frames = bytearray()
        for s in samples:
            val = int(max(-32767, min(32767, s * 32767)))
            frames.extend(struct.pack('<h', val))
        
        wav_file.writeframesraw(frames)

def generate_eat_sound() -> list[float]:
    """Suono quando il serpente mangia una mela (tono ascendente rapido)."""
    duration = 0.12
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = 400 + (t / duration) * 450
        envelope = (1.0 - (t / duration) ** 0.8)
        phase = 2 * math.pi * freq * t
        sine_val = math.sin(phase)
        tri_val = 2 * abs(2 * (freq * t - math.floor(freq * t + 0.5))) - 1
        sample = (0.7 * sine_val + 0.3 * tri_val) * envelope * 0.7
        samples.append(sample)
        
    return samples

def generate_bonus_sound() -> list[float]:
    """Suono quando si raccoglie un frutto bonus (arpeggio squillante)."""
    duration = 0.35
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    notes = [523.25, 659.25, 783.99, 1046.50]
    note_duration = duration / len(notes)
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        note_idx = min(int(t / note_duration), len(notes) - 1)
        freq = notes[note_idx]
        local_t = t - (note_idx * note_duration)
        
        env = (1.0 - (local_t / note_duration) ** 0.5)
        phase = 2 * math.pi * freq * t
        val = 0.6 * math.sin(phase) + 0.3 * (1.0 if math.sin(phase) >= 0 else -1.0)
        sample = val * env * 0.6
        samples.append(sample)
        
    return samples

def generate_game_over_sound() -> list[float]:
    """Suono di Game Over (tono discendente drammatico)."""
    duration = 0.65
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        base_freq = 440 * (1.0 - (t / duration) * 0.75)
        vibrato = math.sin(2 * math.pi * 15 * t) * 15
        freq = max(50, base_freq + vibrato)
        
        envelope = (1.0 - (t / duration) ** 0.6)
        phase = 2 * math.pi * freq * t
        saw_val = 2 * (freq * t - math.floor(freq * t + 0.5))
        sine_val = math.sin(phase)
        sample = (0.5 * saw_val + 0.5 * sine_val) * envelope * 0.65
        samples.append(sample)
        
    return samples

def generate_click_sound() -> list[float]:
    """Suono per click su menu."""
    duration = 0.04
    num_samples = int(SAMPLE_RATE * duration)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        freq = 900 - (t / duration) * 400
        env = 1.0 - (t / duration)
        sample = math.sin(2 * math.pi * freq * t) * env * 0.4
        samples.append(sample)
        
    return samples

def generate_all_sounds(base_dir: str):
    """Genera tutti gli asset sonori nella cartella specificata."""
    sound_dir = os.path.join(base_dir, "assets", "sounds")
    os.makedirs(sound_dir, exist_ok=True)
    
    write_wav(os.path.join(sound_dir, "eat.wav"), generate_eat_sound())
    write_wav(os.path.join(sound_dir, "bonus.wav"), generate_bonus_sound())
    write_wav(os.path.join(sound_dir, "game_over.wav"), generate_game_over_sound())
    write_wav(os.path.join(sound_dir, "click.wav"), generate_click_sound())
    print(f"Effetti sonori generati con successo in: {sound_dir}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    generate_all_sounds(current_dir)
