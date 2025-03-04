from src.model.receipt import Receipt
from src.exceptions import ReceiptNotFound, ReceiptIsDuplicate

class ReceiptStorage:
    def __init__(self):
        self.receipt_storage = {}
        # to check for duplication on retailer+purchase_date_time
        # simulates another unique index on the table
        self.receipt_identifier = {}

    def is_duplicate(self, receipt):
        return receipt.identifier_tuple() in self.receipt_identifier

    def process_receipt(self, input_data):
        receipt = Receipt(**input_data)
        if self.is_duplicate(receipt):
            raise ReceiptIsDuplicate(f'Provided receipt is duplicate: {str(receipt.identifier_tuple())}')

        receipt_id = receipt.receipt_id
        self.receipt_storage[receipt_id] = receipt.to_dict()
        self.receipt_identifier[receipt.identifier_tuple()] = receipt_id
        return receipt_id, self.get_receipt(receipt_id)

    def get_receipt(self, receipt_id):
        if receipt_id in self.receipt_storage:
            return self.receipt_storage[receipt_id]

        raise ReceiptNotFound(receipt_id)

    def get_receipt_dict(self, receipt_id):
        receipt = self.get_receipt(receipt_id)
        # Create a new dictionary to avoid modifying the original
        receipt_copy = receipt.copy()
        receipt_copy['purchaseDateTime'] = Receipt.format_receipt_date(receipt['purchaseDateTime'])
        return receipt_copy

    def get_receipt_points(self, receipt_id):
        if receipt_id in self.receipt_storage:
            return self.receipt_storage[receipt_id]["points"]

        raise ReceiptNotFound(receipt_id)

    def is_in(self, receipt_id):
        return receipt_id in self.receipt_storage

    def clear(self):
        self.receipt_storage.clear()
        self.receipt_identifier.clear()

    def __len__(self):
        return len(self.receipt_storage)
