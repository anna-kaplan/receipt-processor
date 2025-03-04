class Config:
    HOST = '0.0.0.0'
    PORT = 5000

class STATUS_CODE:  # pylint: disable=invalid-name
    SUCCESS = 200
    UNKNOWN_ERROR = 500
    INPUT_ERROR = 400
    NO_RECORD_FOUND = 404

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'
DT_FORMAT = f"{DATE_FORMAT} {TIME_FORMAT}"
