from typing import TypeAlias, Tuple, Any
from pathlib import Path
import logging
import hashlib
import flask
import ast

# Internal imports
import src.api.errors as errs
from src.config.env import EnvConfig
from src.cloner.main import VoiceCloner

app = flask.Flask(__name__)
cfg = EnvConfig()
voice_cloner: VoiceCloner = None # The cloner object

Response: TypeAlias = Tuple[dict, int] # Just a type alias for the response

DEFAULT_PATH = 'lele.wav'

def run_api(_voice_cloner: VoiceCloner) -> None:
    """
    Runs the API for serving feature extraction method
    """
    
    global voice_cloner
    
    voice_cloner = _voice_cloner
    app.run(port=cfg.api_port, debug=True)

@app.route("/integrations/voice-cloning/generate", methods=["POST"])
def generate_voice() -> None:
    def jsonify_error(err: errs.ErrorResponse) -> Response:
        json_err, status_code = err
        return flask.jsonify(json_err), status_code
    
    # Asserting that the request has the necessary data
    def validate_request() -> bool:
        if "data" not in flask.request.json:
            return False
        data = flask.request.json["data"]
        if "attributes" not in data:
            return False
        attributes = data["attributes"]
        return "text" in attributes

    if not validate_request():
        logging.error("Bad request!")
        return jsonify_error(errs.BAD_REQUEST)
    
    # Getting attributes
    attributes = flask.request.json["data"]["attributes"]
    text = attributes["text"]
    
    # Cloning the voice
    try:
        voice = voice_cloner.save_voice_locally(text, Path(DEFAULT_PATH))
    except Exception as exception:
        logging.error(f"Failed to process the image: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
    # Updating that the claim was submitted
    try:
        return flask.send_file(Path('../../' + DEFAULT_PATH), as_attachment=True, mimetype='audio/wav', download_name='lele.wav')
    except Exception as exception:
        logging.error(f"Failed while finalizing the request: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    