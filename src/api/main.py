from typing import TypeAlias, Tuple
import logging
import hashlib
import flask
import ast

import src.api.errors as errs
from src.api.comparison import get_claim_from_embedding
from src.extractor.embedding import FeatureExtractor, FaceExtractionStatus, DiscretizedFeatureVector, FeatureVector
from src.extractor.base64 import decode_base64
from src.config.env import EnvConfig
from src.issuer.connector import IssuerConnector
from src.model.claim import Claim

app = flask.Flask(__name__)
cfg = EnvConfig()

Response: TypeAlias = Tuple[dict, int] # Just a type alias for the response

def run_api() -> None:
    """
    Runs the API for serving feature extraction method
    """
    
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
        voice = CLONER.clone_voice(text)
    except Exception as exception:
        logging.error(f"Failed to process the image: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
    # Saving the claim to the database
    try:
        emb_string = str(emb)
        emb_hash = hashlib.sha256(emb_string.encode()).hexdigest()
        
        if not is_revoke:
            claim = Claim.create(user_id=user_id, 
                                vector=emb_string, 
                                metadata=metadata, 
                                pk=public_key, 
                                claim_id="",
                                is_submitted=False)
            claim.save()
    except Exception as exception:
        logging.error(f"Failed to save the claim: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
    # Making request to the issuer
    try:
        claim_id = connector.create_credential({
            "user_id": user_id,
            "embedding": emb_hash,
            "public_key": public_key,
            "did": did,
            "metadata": metadata
        })
    except Exception as exception:
        logging.error(f"Failed to send data to the issuer: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
    # Updating that the claim was submitted
    try:
        str_to_update = emb_string if not is_revoke else closest_claim['vector']
        q = Claim.update(is_submitted=True, claim_id=claim_id).where(Claim.vector == str_to_update)
        q.execute()
        logging.error('7')
        # TODO: make in a single update
        if is_revoke:
            q = Claim.update(user_id=user_id, 
                vector=emb_string, 
                metadata=metadata, 
                pk=public_key).where(Claim.vector == closest_claim['vector'])
            q.execute()
        
        response_user_id = None
        if is_revoke:
            response_user_id = closest_claim['user_id']
        return form_extract_response(emb_string, claim_id=claim_id, user_id=response_user_id)
    except Exception as exception:
        logging.error(f"Failed while finalizing the request: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)
    
@app.route("/integrations/face-extractor-svc/pk-from-image", methods=["POST"])
def get_public_key_from_image() -> None:
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
        return "image" in attributes

    if not validate_request():
        logging.error("Bad request!")
        return jsonify_error(errs.BAD_REQUEST)
    
    # Getting attributes
    attributes = flask.request.json["data"]["attributes"]
    image_base64 = attributes["image"]
    
    # Decoding the image and processing it
    try:
        img = decode_base64(image_base64)
        extractor = FeatureExtractor(img)
        emb, status = extractor.extract_features()
        # Returning the status if something bad happenned
        match status:
            case FaceExtractionStatus.NO_FACE_FOUND:
                return jsonify_error(errs.NO_FACE_FOUND)
            case FaceExtractionStatus.TOO_MANY_PEOPLE:
                return jsonify_error(errs.TOO_MANY_PEOPLE)
        
        # Verifying that the claim does exist
        closest_claim = get_claim_from_embedding(emb)
        claim_exists = closest_claim is not None
        
        if not claim_exists:
            return jsonify_error(errs.ACCOUNT_DOES_NOT_EXIST)
    except Exception as exception:
        logging.error(f"Failed to process the image: {exception}")
        return jsonify_error(errs.INTERNAL_ERROR)

    return form_pk_response(closest_claim['pk'], closest_claim['metadata'], closest_claim['user_id'])
        
def form_extract_response(embedding: DiscretizedFeatureVector, claim_id: int, user_id: str = None) -> Response:
    """
    Formats the response to be returned by the API.
    If the `user_id` is None, it means that revoke did not happen.
    """
    
    response = {
        "data": {
            "id" : 1,
            "type": "embedding",
            "attributes": {
                "embedding": embedding,
                "claim_id": claim_id,
            }
        }
    }
    if user_id is not None:
        # Adding user id to the response
        response["data"]["attributes"]["user_id"] = user_id

    return response, 200
    
 
def form_pk_response(public_key: str, metadata: str, user_id: str) -> Response:
    """
    Formats the response to be returned by the API.
    """
    
    return flask.jsonify({
        "data": {
            "id" : 1,
            "type": "pk",
            "attributes": {
                "public_key": public_key,
                "metadata": metadata,
                "user_id": user_id
            }
        }
    }), 200
