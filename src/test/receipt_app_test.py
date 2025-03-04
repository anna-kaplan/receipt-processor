import unittest
from unittest.mock import patch, Mock
from flask import json

from src.receipt_app import app, receipt_storage # type: ignore
from src.config import STATUS_CODE

valid_receipt = {
    "retailer": "Walgreens",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "08:13",
    "total": "2.65",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
        {"shortDescription": "Dasani", "price": "1.40"}
    ]
}

class ReceiptProcessingTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        self.receipt_storage = receipt_storage
        self.receipt_storage.clear()

    def test_process_receipt_valid_input(self):
        response = self.app.post('/receipts/process', json=valid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.SUCCESS)
        data = json.loads(response.data)
        self.assertIn('id', data)
        receipt_id = data['id']
        self.assertTrue(self.receipt_storage.is_in(receipt_id))
        self.assertEqual(self.receipt_storage.get_receipt_points(receipt_id), 15)

        points_response = self.app.get(f'/receipts/{receipt_id}/points')
        self.assertEqual(points_response.status_code, STATUS_CODE.SUCCESS)
        points_data = json.loads(points_response.data)
        self.assertEqual(points_data, {'points': 15})

        receipt_response = self.app.get(f'/receipts/{receipt_id}')
        self.assertEqual(receipt_response.status_code, STATUS_CODE.SUCCESS)
        receipt_data = json.loads(receipt_response.data)

        self.assertEqual(receipt_data['receipt']['points'], 15)
        self.assertEqual(receipt_data['receipt']['id'], receipt_id)
        self.assertEqual(receipt_data['receipt']['retailer'], valid_receipt['retailer'])
        self.assertEqual(receipt_data['receipt']['total'], float(valid_receipt['total']))
        self.assertEqual(
            receipt_data['receipt']['purchaseDateTime'],
            valid_receipt['purchaseDate'] + ' ' + valid_receipt['purchaseTime']
        )
        def parse_price(item):
            return {key: float(val) if key == 'price' else val for key, val in item.items()}
        self.assertEqual(
            receipt_data['receipt']['items'],
            [parse_price(item) for item in valid_receipt['items']]
        )

    def test_process_duplicate(self):
        response = self.app.post('/receipts/process', json=valid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.SUCCESS)

        duplicate = self.app.post('/receipts/process', json=valid_receipt)
        self.assertEqual(duplicate.status_code, STATUS_CODE.INPUT_ERROR)
        self.assertEqual(
            json.loads(duplicate.data.decode('utf-8'))['message'],
            "Provided receipt is duplicate: ('Walgreens', '2022-01-02 08:13')"
        )

    def test_process_receipt_invalid_retailer(self):
        invalid_receipt = {
            "retailer": "Target!",  # Invalid character
            "purchaseDate": "2023-10-27",
            "purchaseTime": "15:30",
            "total": "2.50",
            "items": [{"shortDescription": "Mu-Mu", "price": "2.50"}]
        }
        response = self.app.post('/receipts/process', json=invalid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.INPUT_ERROR)
        self.assertTrue('Target!' in response.data.decode('utf-8'))

    def test_process_receipt_invalid_total_format(self):
        invalid_receipt = {
            "retailer": "Target",
            "purchaseDate": "2023-10-27",
            "purchaseTime": "15:30",
            "total": "25.755",  # Invalid format
            "items": [{"shortDescription": "Mu-Mu", "price": "2.755"}]
        }
        response = self.app.post('/receipts/process', json=invalid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.INPUT_ERROR)
        self.assertTrue('total' in response.data.decode('utf-8'))

    def test_get_points_invalid_id(self):
        response = self.app.get('/receipts/invalid_id/points')
        self.assertEqual(response.status_code, STATUS_CODE.NO_RECORD_FOUND)
        data = json.loads(response.data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'No receipt found with id=invalid_id')

    def test_process_receipt_invalid_json(self):
        """Test processing receipt with invalid JSON input"""
        response = self.app.post('/receipts/process',
                                 data="invalid_json",
                                 content_type='application/json'
                                 )
        self.assertEqual(response.status_code, STATUS_CODE.INPUT_ERROR)
        self.assertIn("Input Error", response.json['message'])

    def test_process_receipt_missing_required_fields(self):
        """Test processing receipt with missing required fields"""
        invalid_receipt = {"retailer": "Target"}  # Missing required fields
        response = self.app.post('/receipts/process',
                                 data=json.dumps(invalid_receipt),
                                 content_type='application/json'
                                 )
        self.assertEqual(response.status_code, STATUS_CODE.INPUT_ERROR)
        self.assertIn("Input Error", response.json['message'])

    def test_get_points_invalid_receipt_id(self):
        """Test fetching points for a non-existent receipt ID"""
        response = self.app.get('/receipts/invalid_id/points')
        self.assertEqual(response.status_code, STATUS_CODE.NO_RECORD_FOUND)
        self.assertIn("No receipt found with id=invalid_id",
                      response.json['message']
                      )

    def test_view_receipt_invalid_receipt_id(self):
        """Test viewing a non-existent receipt"""
        response = self.app.get('/receipts/invalid_id')
        self.assertEqual(response.status_code, STATUS_CODE.NO_RECORD_FOUND)
        self.assertIn("No receipt found with id=invalid_id",
                      response.json['message']
                      )

    def test_process_server_error_receipt_internal(self):
        """Mock an internal error in receipt processing"""
        with patch('src.receipt_storage.ReceiptStorage.process_receipt',
                   side_effect=Exception("Mocked failure")) as mock_response:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json = {'message': 'Mocked failure'}

            with patch('flask.Flask.post', return_value=mock_response):
                response = self.app.post('/receipts/process', data=json.dumps(valid_receipt),
                                         content_type='application/json'
                                         )
                self.assertEqual(response.status_code, STATUS_CODE.UNKNOWN_ERROR)
                self.assertEqual(response.json['message'],
                                 'An error occurred during receipt processing - Mocked failure'
                                )

    def test_process_server_error_get_poinst(self):
        response = self.app.post('/receipts/process', json=valid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.SUCCESS)
        data = json.loads(response.data)
        receipt_id = data['id']

        with patch('src.receipt_storage.ReceiptStorage.get_receipt_points',
                   side_effect=Exception("Mocked failure")) as mock_response:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json = {"message": "Mocked failure"}
            with patch ('flask.Flask.get', return_value=mock_response):
                get_response = self.app.get(f'/receipts/{receipt_id}/points',
                                            content_type='application/json'
                                            )
                self.assertEqual(get_response.status_code, STATUS_CODE.UNKNOWN_ERROR)
                self.assertEqual(get_response.json['message'], 'An unexpected error occurred.')

    def test_process_server_error_view_receipt(self):
        response = self.app.post('/receipts/process', json=valid_receipt)
        self.assertEqual(response.status_code, STATUS_CODE.SUCCESS)
        data = json.loads(response.data)
        receipt_id = data['id']

        with patch('src.receipt_storage.ReceiptStorage.get_receipt_dict',
                   side_effect=Exception("Mocked failure")) as mock_response:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.json = {"message": "Mocked failure"}
            with patch ('flask.Flask.get', return_value=mock_response):
                view_response = self.app.get(f'/receipts/{receipt_id}',
                                             content_type='application/json'
                                             )
                self.assertEqual(view_response.status_code, STATUS_CODE.UNKNOWN_ERROR)
                self.assertEqual(view_response.json['message'], 'An unexpected error occurred.')


if __name__ == '__main__':
    unittest.main()

