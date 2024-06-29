from typing import List

SPEAKER_WAV = [
    'voices/lele/1.wav',
    'voices/lele/2.wav',
    'voices/lele/3.wav',
    'voices/lele/4.wav',
    'voices/lele/5.wav',
]

def get_speaker_wav() -> List[str]:
    """
    Returns the speaker wav files
    """
    
    return SPEAKER_WAV