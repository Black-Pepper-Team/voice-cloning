import typer
import src.api.main as api
import src.cloner.main as cloner

app = typer.Typer(help="Voice Cloning API for the pAIrates team")

@app.command()
def debug() -> None:
    """Debugs the service"""
    
    TEST_TEXT = "Hello, my name is Ivan and I love balls"
    TEST_PATH = "test.wav"
    cloner.VoiceCloner().save_voice_locally(TEST_TEXT, TEST_PATH)

@app.command()
def run_api() -> None:
    """Runs the service API"""

    voice_cloner = cloner.VoiceCloner()
    api.run_api(voice_cloner)
    
if __name__ == '__main__':
    app()
    
