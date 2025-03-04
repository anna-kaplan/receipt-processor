import unittest
import datetime

from src.config import DATE_FORMAT, DT_FORMAT
from src.model.points_calculator import PointsCalculator
from src.receipt_storage import ReceiptStorage, Receipt

valid_receipt = {
    "retailer": "Walgreens",
    "purchaseDate": "2022-01-02",
    "purchaseTime": "08:13",
    "total": "2.65",
    "items": [
        {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
        {"shortDescription": "Dasani", "price": "1.40"},
    ],
}

class ReceiptStorageTests(unittest.TestCase):
    def setUp(self):
        self.receipt_storage = ReceiptStorage()

    def tearDown(self):
        self.receipt_storage.clear()
        super().tearDown()

    def test_process_receipt(self):
        receipt_id, result = self.receipt_storage.process_receipt(valid_receipt)
        self.assertEqual(len(self.receipt_storage), 1)

        self.assertEqual(result["retailer"], valid_receipt["retailer"])
        self.assertEqual(result["total"], float(valid_receipt["total"]))

        date_time_string = "{} {}".format(valid_receipt["purchaseDate"], valid_receipt["purchaseTime"])
        self.assertEqual(
            result["purchaseDateTime"],
            datetime.datetime.strptime(date_time_string, DT_FORMAT)
        )

        self.assertEqual(len(result["items"]), len(valid_receipt["items"]), "Number of items does not match")
        self.assertEqual(
            [r["shortDescription"] for r in result["items"]],
            [p["shortDescription"] for p in valid_receipt["items"]]
        )
        self.assertEqual(
            [r["price"] for r in result["items"]],
            [float(p["price"]) for p in valid_receipt["items"]]
        )
        self.assertEqual(result["points"], 15, "Points do not match")

        view_receipt = self.receipt_storage.get_receipt(receipt_id)
        self.assertEqual(result, view_receipt)
        self.assertEqual(self.receipt_storage.get_receipt_points(receipt_id), 15)

    def test_process_duplicate(self):
        self.receipt_storage.process_receipt(valid_receipt)
        self.assertEqual(len(self.receipt_storage), 1)
        with self.assertRaises(Exception, msg="Process Duplicate") as context:
            self.receipt_storage.process_receipt(valid_receipt)
        self.assertEqual(
            str(context.exception),
            "Provided receipt is duplicate: ('Walgreens', '2022-01-02 08:13')"
        )

    def test_calculate_receipt_points(self):
        recipt_data = {
            "retailer": "Target",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "13:01",
            "items": [
                {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
                {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
                {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
                {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
                {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
            ],
            "total": "35.35",
        }
        processed_receipt = Receipt(**recipt_data)
        self.assertEqual(processed_receipt.points, 28)
        rule_points = PointsCalculator.parse_rules(processed_receipt)
        self.assertEqual(rule_points, {
            'retailer_alnum': 6,
            'total_round_dollar': 0,
            'total_in_quarters': 0,
            'each_pair_of_items_5c': 10,
            'items_names_in3': 6,
            'odd_day': 6,
            'special_time': 0,
        }, "Rule points calculation is incorrect")

    def test_calculate_receipt_points_multiple_of_25_daytime(self):
        receipt_data = {
            "retailer": "Argent",
            "purchaseDate": "2022-01-01",
            "purchaseTime": "15:01",
            "items": [
                {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
                {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
                {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
                {"shortDescription": "Doritos Nacho Cheese", "price": "3.00"},
                {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
            ],
            "total": "35.00",
        }
        receipt = Receipt(**receipt_data)
        self.assertEqual(receipt.points, 113)
        rule_points = PointsCalculator.parse_rules(receipt)
        self.assertEqual(rule_points, {
            'retailer_alnum': 6,
            'total_round_dollar': 50,
            'total_in_quarters': 25,
            'each_pair_of_items_5c': 10,
            'items_names_in3': 6,
            'odd_day': 6,
            'special_time': 10
        })

    def test_get_receipt_invalid_id(self):
        receipt_id = "invalid_id"
        with self.assertRaises(Exception, msg="Expected an exception for invalid receipt ID") as context:
            self.receipt_storage.get_receipt(receipt_id)
        self.assertEqual(str(context.exception), "No receipt found with id=invalid_id")

    def test_get_points_invalid_id(self):
        receipt_id = "invalid_id"
        with self.assertRaises(Exception, msg="Expected an exception for invalid receipt ID") as context:
            self.receipt_storage.get_receipt_points(receipt_id)
        self.assertEqual(str(context.exception), "No receipt found with id=invalid_id")

    def test_receipt_with_future_date(self):
        future_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(DATE_FORMAT)
        purchase_time = "12:30"
        receipt_data = {
            "retailer": "Target",
            "purchaseDate": future_date,
            "purchaseTime": purchase_time,
            "total": "20.00",
            "items": [
                {"shortDescription": "Milk", "price": "4.00"},
                {"shortDescription": "Bread", "price": "3.00"}
            ]
        }

        with self.assertRaises(ValueError, msg="Expected ValueError for future purchase date") as context:
            Receipt(**receipt_data)
        self.assertEqual(str(context.exception), "Purchase date cannot be in the future")

if __name__ == "__main__":
    unittest.main()
