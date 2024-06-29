from typing import Tuple, TypeAlias

ErrorResponse: TypeAlias = Tuple[dict, int]

INTERNAL_ERROR: ErrorResponse = ({
        "errors": [
            {
                "title": "Something bad happened",
                "status" : "500",
                "meta": "Contact Dima and tell him to fix it"
            }
        ]
    }, 500)

INVALID_METHOD: ErrorResponse = ({
        "errors": [
            {
                "title": "Invalid request method",
                "status" : "405",
                "meta": "Only POST requests are allowed."
            }
        ]
    }, 405)

BAD_REQUEST: ErrorResponse = ({
    "errors": [
            {
                "code": "400",
                "title": "Bad Request",
                "meta": "Data is incorrectly structured"
            }
        ]
    }, 400)

ACCOUNT_ALREADY_EXISTS: ErrorResponse = ({
    "errors": [
        {
            "code": "400",
            "title": "Bad Request",
            "meta": "Account already exists"
        }
    ]
}, 400)

ACCOUNT_DOES_NOT_EXIST: ErrorResponse = ({
    "errors": [
        {
            "code": "400",
            "title": "Bad Request",
            "meta": "Account does not exist"
        }
    ]
}, 403)

NO_FACE_FOUND: ErrorResponse = ({
    "errors": [
            {
                "code": "400",
                "title": "No face found",
                "meta": "No face found in the image"
            }
        ]
    }, 403)

TOO_MANY_PEOPLE: ErrorResponse = ({
        "errors": [
            {
                "code": "400",
                "title": "Too many people",
                "meta": "Too many people found in the image"
            }
        ]
    }, 403)
