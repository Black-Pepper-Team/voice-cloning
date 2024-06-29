import __future__
import time
import logging
from pathlib import Path
from typing import Any
from TTS.api import TTS
import os

# Internal imports
from voices.voices import get_speaker_wav

class VoiceCloner:
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self) -> None:
        """
        Initializes the VoiceCloner class
        """
        
        self._tts = TTS('xtts-v2')
    
    def clone_voice(self, text: str) -> Any:
        """
        Clones the voice from the given text
        
        Input:
        - text: str - The text to clone
        
        Output:
        - Any - The cloned voice
        """
        
        start_time = time.time() # Recoding how much tome it takes to clone the voice
        voice = self._tts.tts(
                text=text,
                speaker_wav=get_speaker_wav(),
                language=VoiceCloner.DEFAULT_LANGUAGE
            )
        end_time = time.time()
        
        # Printing the time taken to clone the voice
        time_taken = end_time - start_time
        logging.info(f"Voice cloned in {time_taken} seconds")
        
        return voice
    
    def save_voice_locally(self, text: str, path: Path) -> None:
        """
        Saves the voice to the local path
        
        Input:
        - text: str - The text to clone
        - path: Path - The path to save the voice
        
        Output:
        - None
        """
        
        if os.path.exists(str(path)):
            os.remove(str(path))
        
        start_time = time.time() # Recoding how much tome it takes to clone the voice
        voice = self._tts.tts_to_file(
                text=text,
                file_path=str(path),
                speaker_wav=get_speaker_wav(),
                language=VoiceCloner.DEFAULT_LANGUAGE
            )
        end_time = time.time()
        
        # Printing the time taken to clone the voice
        time_taken = end_time - start_time
        logging.info(f"Voice cloned in {time_taken} seconds")
        
        return voice
    