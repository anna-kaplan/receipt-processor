from src.config import DATE_FORMAT, TIME_FORMAT

schema_patterns = {
    DATE_FORMAT: r"^\d{4}-\d{2}-\d{2}$",
    TIME_FORMAT: r"^\d{2}:\d{2}$"
    }

request_schema = {
    'type': 'object',
    'properties': {
        'retailer': {'type': 'string', 'pattern': "^[\\w\\s\\-&]+$"},
        'purchaseDate': {'type': 'string', 'pattern': schema_patterns[DATE_FORMAT]},
        'purchaseTime': {'type': 'string', 'pattern': schema_patterns[TIME_FORMAT]},
        'items': {
            'type' : 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'shortDescription': {'type': 'string', 'pattern': "^[\\w\\s\\-]+$"},
                    'price': {'type': 'string', 'pattern': "^\\d+\\.\\d{2}$"}
                },
                'required': ['shortDescription', 'price']
            },
            'minItems': 1  # to ensure at least one item,
        },
        'total':  {'type': 'string', 'pattern': "^\\d+\\.\\d{2}$"}
    },
    'required': ['retailer', 'purchaseDate', 'purchaseTime', 'total', 'items']
}
