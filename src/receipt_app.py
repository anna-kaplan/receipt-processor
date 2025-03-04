from flask import Flask, request, jsonify
from flask_expects_json import expects_json
import logging

from src.config import Config, STATUS_CODE
from src.receipt_storage import ReceiptStorage
from src.validation_schema import request_schema
from src.exceptions import ReceiptNotFound, ReceiptIsDuplicate

app = Flask(__name__)

# AK Note: simplified logging: for prod process should be saved in log file
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

receipt_storage = ReceiptStorage()


@app.errorhandler(STATUS_CODE.INPUT_ERROR)
def handle_invalid_json(error):
    return jsonify({'message': f'Input Error {str(error)}'}), STATUS_CODE.INPUT_ERROR


@app.route('/receipts/process', methods=['POST'])
@expects_json(request_schema)  # verifies json, otherwise returns status_code = 400 STATUS_CODE.INPUT_ERROR
def process_receipt():
    try:
        receipt_id, _ = receipt_storage.process_receipt(request.get_json())
        logger.info(f'Processed receipt, id={receipt_id}')

        return jsonify({'id': receipt_id}), STATUS_CODE.SUCCESS
    except ReceiptIsDuplicate as e:
        message = str(e)
        logger.error(str(e))
        return jsonify({'message': message}), STATUS_CODE.INPUT_ERROR
    except Exception as e:
        message = f'An error occurred during receipt processing - {str(e)}'
        logger.error(message)
        return jsonify({'message': message}), STATUS_CODE.UNKNOWN_ERROR


@app.route('/receipts/<receipt_id>/points', methods=['GET'])
def get_points(receipt_id):
    try:
        receipt_points = receipt_storage.get_receipt_points(receipt_id)
        return jsonify({'points': receipt_points}), STATUS_CODE.SUCCESS
    except ReceiptNotFound as e:
        logger.error(e.message)
        return jsonify({'message': e.message}), STATUS_CODE.NO_RECORD_FOUND
    except Exception as e:
        message = f'An unexpected error occurred while retrieving points for receipt ID={receipt_id} - {str(e)}'
        logger.error(message)
        return jsonify({'message': 'An unexpected error occurred.'}), STATUS_CODE.UNKNOWN_ERROR


@app.route('/receipts/<receipt_id>', methods=['GET'])
def view_receipt(receipt_id):
    try:
        receipt = receipt_storage.get_receipt_dict(receipt_id)
        return jsonify({'receipt': receipt}), STATUS_CODE.SUCCESS
    except ReceiptNotFound as e:
        logger.error(e.message)
        return jsonify({'message': e.message}), STATUS_CODE.NO_RECORD_FOUND
    except Exception as e:
        message = f'An unexpected error occurred while retrieving receipt ID={receipt_id} - {str(e)}'
        logger.error(message)
        return jsonify({'message': 'An unexpected error occurred.'}), STATUS_CODE.UNKNOWN_ERROR


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT)
