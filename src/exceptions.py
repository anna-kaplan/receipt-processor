class ReceiptNotFound(Exception):
    def __init__(self, receipt_id):
        self.message = f"No receipt found with id={receipt_id}"
        super().__init__(self.message)

class ReceiptIsDuplicate(Exception):
    pass
