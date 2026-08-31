from playsound import playsound
import threading
import os
from pathlib import Path
 
class AudioService:
    def __init__(self):
        self.beep_sound_path = str(Path(__file__).parent.parent / "assets" / "beep.wav")
        self._ensure_beep_sound_exists()
        
    def _ensure_beep_sound_exists(self):
        """Ensure the beep sound file exists"""
        os.makedirs(os.path.dirname(self.beep_sound_path), exist_ok=True)
        if not os.path.exists(self.beep_sound_path):
            # Create a simple beep sound using a sine wave
            import numpy as np
            from scipy.io import wavfile
            
            sample_rate = 44100
            duration = 0.5  # seconds
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            note = np.sin(2 * np.pi * 440 * t)
            audio = note * 32767
            audio = audio.astype(np.int16)
            wavfile.write(self.beep_sound_path, sample_rate, audio)
    
    def play_beep(self):
        """Play beep sound in a separate thread"""
        threading.Thread(target=playsound, args=(self.beep_sound_path,), daemon=True).start()