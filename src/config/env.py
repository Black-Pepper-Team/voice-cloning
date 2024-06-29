from __future__ import annotations

import os
from dotenv import load_dotenv

class EnvConfig:
    """Class responsible for loading environment variables"""
    
    DEFAULT_PORT = 5050
    
    def __init__(self) -> None:
        self._load_env()
        
    def _load_env(self) -> None:
        """
        Loads environment variables
        """
        
        dotenv_path = os.getenv('DOTENV_FILE')
        load_dotenv(dotenv_path=dotenv_path)
        
        self._port = os.getenv('PORT')
        assert self._port is not None, 'port cannot be empty'
        if self._port is None:
            self._port = EnvConfig.DEFAULT_PORT
            
    @property
    def api_port(self) -> int:
        """
        Returns the API port
        """
        
        return self._port