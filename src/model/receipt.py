import datetime
import uuid

from src.config import DT_FORMAT
from src.model.points_calculator import PointsCalculator

RECEIPT_ID_NAME = 'id'


class Receipt:
    """
    The Receipt class represents a receipt object.
    It handles parsing date/time, item details, and calculates points using the PointsCalculator.
    """
    def __init__(self, **kwargs):
        # simplified version of Receipt with items as a dictionary
        self.retailer, self.purchase_date, self.purchase_time, self.total, self.items = [
            kwargs.get(name) for  name
            in ['retailer', 'purchaseDate', 'purchaseTime', 'total', 'items']]
        if not all([self.retailer,
                    self.purchase_date,
                    self.purchase_time,
                    self.total,
                    self.items,len(self.items) > 1
                    ]):
            raise ValueError("Invalid Receipt")

        self.receipt_id = str(uuid.uuid4())
        self.purchase_date_time = self._parse_datetime(self.purchase_date, self.purchase_time)
        if self.purchase_date_time > datetime.datetime.now():
            # TODO date validations; how far back can it go (settings?)
            raise ValueError("Purchase date cannot be in the future")
        self.total = float(self.total)
        self.items = self._parse_items(self.items)

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
            RECEIPT_ID_NAME: self.receipt_id,
            "retailer": self.retailer,
            "purchaseDateTime": self.purchase_date_time,
            "total": self.total,
            "items": self.items,
            "points": self.points,
        }

    @staticmethod
    def format_receipt_date(dt, fmt=DT_FORMAT):
        """
        Formats receipt purchase_date_time,  uses default format is no format is specified
        """
        return dt.strftime(fmt)
