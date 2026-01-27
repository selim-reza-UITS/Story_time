from io import BytesIO
from pocket_tts import TTSModel
import scipy.io.wavfile
import torch
import os

class TTSClient:
    def __init__(self):
        """
        Initialize the Pocket TTS model.
        """
        self.tts_model = None
        self.voice_state = None

    def _ensure_model_loaded(self):
        if not self.tts_model:
            print("Loading Pocket TTS model...")
            try:
                self.tts_model = TTSModel.load_model()
                self.voice_state = self.tts_model.get_state_for_audio_prompt("alba")
                print("Pocket TTS model loaded successfully.")
            except Exception as e:
                print(f"Failed to initialize Pocket TTS: {e}")
                self.tts_model = None

    def text_to_speech(self, text: str) -> bytes:
        """
        Converts text to speech audio bytes using Pocket TTS.
        returns: WAV file bytes
        """
        self._ensure_model_loaded()
        
        if not text or not self.tts_model:
            return b""
            
        try:
            # Generate audio tensor
            audio_tensor = self.tts_model.generate_audio(self.voice_state, text)
            
            # Convert to bytes
            fp = BytesIO()
            # Write wav to memory buffer. 
            # audio_tensor is a torch tensor, we need numpy array for scipy
            scipy.io.wavfile.write(fp, self.tts_model.sample_rate, audio_tensor.numpy())
            fp.seek(0)
            
            return fp.read()
            
        except Exception as e:
            print(f"TTS Generation Error: {e}")
            return b""
