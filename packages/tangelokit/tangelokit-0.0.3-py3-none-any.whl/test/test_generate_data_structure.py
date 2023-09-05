import unittest
from tangelokit import GenerateDataStructure


class TestGenerateDataStructure(unittest.TestCase):
    def test_validator_information(self):
        credit_line = {
            "uid": "1",
            "created_at": "2023-08-30",
            "balance": 23,
            "todayToPay": {
                "value": 497819.23,
                "total": 582662.65,
                "date": "2023-08-30",
                "last_quota": 448773.98
            }
        }
        disbursements = [
            {
                "uid": "23232",
                "uuid": "32323432",
                "start_date": "2020-02-02",
                "created_at": "2020-01-02",
                "principal": 23232,
                "days_late": 222,
                "status": "disbursed",
                "quotas": [],
                "resumen": {
                    "last_quota": 2323,
                    "total": 784,
                    "value": 4565
                }
            },
            {
                "uid": "23232",
                "uuid": "32323432",
                "start_date": "2020-02-02",
                "created_at": "2020-01-02",
                "principal": 23232,
                "days_late": 222,
                "status": "disbursed",
                "quotas": [],
                "resumen": {
                    "last_quota": 2323,
                    "total": 784,
                    "value": 4565
                }
            }
        ]
        product = {
            "uuid": "22",
            "period":  {
                "type": "month",
                "holidays": "holidays"
            }
        }
        contact = {
            "cc": "22"
        }

        credit_request = {
            "code": "22",
            "approve_amount": 2
        }
        result = GenerateDataStructure(
            credit_line=credit_line,
            credit_request=credit_request,
            contact=contact,
            disbursements=disbursements,
            product=product
        )
        self.assertEqual(result.errors, [])
        result_expected = {
            "total": 1568,
            "value": 9130,
            "moratorium_amount": 4646,
            "quotas_in_arrears": 0,
            "days_late": 222,
            "product_uuid": "22",
            "product_name": "",
            "disbursements": [
                {
                    "uid": "23232",
                    "uuid": "32323432",
                    "start_date": "2020-02-02",
                    "created_at": "2020-01-02",
                    "principal": 23232,
                    "days_late": 222,
                    "status": "",
                    "quotas": [

                    ],
                    "resumen":{
                        "last_quota": 2323,
                        "total": 784,
                        "value": 4565
                    },
                    "quotas_in_arrears": 0,
                    "expiration_date": "N/A",
                    "payment_date": "2023-08-30",
                    "moratorium_amount": 2323,
                    "periods": {
                        "periodicy": "month"
                    },
                    "todayToPay": {
                        "value": 497819.23,
                        "total": 582662.65,
                        "date": "2023-08-30",
                        "last_quota": 448773.98
                    }
                },
                {
                    "uid": "23232",
                    "uuid": "32323432",
                    "start_date": "2020-02-02",
                    "created_at": "2020-01-02",
                    "principal": 23232,
                    "days_late": 222,
                    "status": "",
                    "quotas": [

                    ],
                    "resumen":{
                        "last_quota": 2323,
                        "total": 784,
                        "value": 4565
                    },
                    "quotas_in_arrears": 0,
                    "expiration_date": "N/A",
                    "payment_date": "2023-08-30",
                    "moratorium_amount": 2323,
                    "periods": {
                        "periodicy": "month"
                    },
                    "todayToPay": {
                        "value": 497819.23,
                        "total": 582662.65,
                        "date": "2023-08-30",
                        "last_quota": 448773.98
                    }
                }
            ],
            "periods": {
                "periodicy": "month"
            },
            "payment_date": "2023-08-30",
            "created_at": "2023-08-30",
            "amount_disbursed": 23,
            "total_disbursement": 46464.0,
            "credit_request": {
                "code": "22",
                "approve_amount": 2,
                "contact": {
                    "cc": "22"
                }
            }
        }
        self.assertDictEqual(result.response, result_expected)
