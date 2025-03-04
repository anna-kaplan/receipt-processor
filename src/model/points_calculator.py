import math

class PointsCalculator:
    # simplified version of points calculator
    rules = {
            "retailer_alnum": {
                'field': 'retailer',
                'method': lambda retailer: sum(1 for char in retailer if char.isalnum()),
            },
            "total_round_dollar": {
                'field': 'total',
                'method': lambda total: 50 if total % 1 == 0 else 0,
            },
            "total_in_quarters": {
                'field': 'total',
                'method': lambda total: 25 if total * 100 % 25 == 0 else 0,
            },
            "each_pair_of_items_5c": {
                'field': 'items',
                'method': lambda items: 5 * (len(items) // 2),
            },
            "items_names_in3": {
                'field': 'items',
                'method': lambda items: sum([math.ceil(0.2 * item["price"]) for item in items
                                    if len(item["shortDescription"].strip()) % 3 == 0
                                    ]),
            },
            "odd_day": {
                'field': 'purchase_date_time',
                'method': lambda purchase_date_time: 6 if purchase_date_time.day % 2 else 0,
            },
            "special_time": {
                'field': 'purchase_date_time',
                'method': lambda purchase_date_time: 10 if 14 <= purchase_date_time.hour < 16 else 0,
            },
        }

    @staticmethod
    def parse_rules(receipt):
        rule_values = {}

        for rule, info in PointsCalculator.rules.items():
            value = getattr(receipt, info['field'])
            rule_values[rule] = info['method'](value)

        return rule_values

    @staticmethod
    def calculate_points(receipt):
        parse_point_rules = PointsCalculator.parse_rules(receipt)
        return sum(parse_point_rules.values())
