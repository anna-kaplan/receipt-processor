import datetime
import uuid

from src.config import DT_FORMAT
from src.model.points_calculator import PointsCalculator

receipt_id_name = 'id'


class Receipt:
    def __init__(self, retailer, purchaseDate, purchaseTime, total, items):
        # simplified version of Receipt with items as a dictionary
        self.receipt_id = str(uuid.uuid4())
        self.retailer = retailer
        self.purchase_date_time = self._parse_datetime(purchaseDate, purchaseTime)
        if self.purchase_date_time > datetime.datetime.now():
            # TODO date validations; how far back can it go (settings?)
            raise ValueError("Purchase date cannot be in the future")
        self.total = float(total)
        self.items = self._parse_items(items)

        self.points = PointsCalculator.calculate_points(self)

    @staticmethod
    def _parse_datetime(date_str, time_str):
        date_time_string = f"{date_str} {time_str}"
        return datetime.datetime.strptime(date_time_string, DT_FORMAT)

    @staticmethod
    def _parse_items(items):
        return [
            {
                "shortDescription": item["shortDescription"].strip(),
                "price": float(item["price"])
            }
            for item in items
        ]

    def identifier_tuple(self):
        return (self.retailer, self.purchase_date_time.strftime(DT_FORMAT))

    def to_dict(self):
        """Convert the Receipt object to a dictionary format for storage."""
        return {
            receipt_id_name: self.receipt_id,
            "retailer": self.retailer,
            "purchaseDateTime": self.purchase_date_time,
            "total": self.total,
            "items": self.items,
            "points": self.points,
        }

    @staticmethod
    def format_receipt_date(dt, fmt=DT_FORMAT):
        return dt.strftime(fmt)
