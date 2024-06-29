from typing import TypeAlias, Tuple, Any
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
    
    # Returning an error if got a wrong method
    if flask.request.method != "POST":
        return jsonify_error(errs.INVALID_METHOD)
    
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
        voice = voice_cloner.clone_voice(text)
    except Exception as exception:
        logging.error(f"Failed to process the image: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
    # Updating that the claim was submitted
    try:
        return flask.send_file(voice, as_attachment=True, mimetype='.wav', download_name='lele.wav')
    except Exception as exception:
        logging.error(f"Failed while finalizing the request: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    