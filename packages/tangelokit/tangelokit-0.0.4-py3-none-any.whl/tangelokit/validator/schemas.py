from tangelokit.common.enums import SchemasTypes
SCHEMAS = {
    SchemasTypes.CREDIT_LINE.value: {
        "type": "object",
        "properties": {
            "uid": {"type": "string"},
            "created_at": {"type": "string", "format": "date"},
            "balance": {"type": "number"},
            "todayToPay": {
                "type": "object",
                "properties": {
                    "value": {"type": "number"},
                    "total": {"type": "number"},
                    "date": {"type": "string", "format": "date"},
                    "last_quota": {"type": "number"}
                },
                "required": ["value", "total", "date", "last_quota"]
            }
        },
        "required": ["uid", "created_at", "balance", "todayToPay"]
    },
    SchemasTypes.DISBURSEMENT.value: {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "uid": {"type": "string"},
                "uuid": {"type": "string"},
                "start_date": {"type": "string", "format": "date"},
                "created_at": {"type": "string", "format": "date"},
                "principal": {"type": "number"},
                "days_late": {"type": "number"},
                "status": {"type": "string", "enum": ["disbursed"]},
                "quotas": {"type": "array"},
                "resumen": {
                    "type": "object",
                    "properties": {
                        "last_quota": {"type": "number"},
                        "total": {"type": "number"},
                        "value": {"type": "number"}
                    },
                    "required": ["last_quota", "total", "value"]
                }
            },
            "required": ["uid", "uuid", "start_date", "created_at", "principal", "days_late", "status", "quotas", "resumen"]
        }
    },
    SchemasTypes.CREDIT_REQUEST.value: {
        "type": "object",
        "properties": {
            "code": {"type": "string"},
            "approve_amount": {"type": "number"},
        },
        "required": ["code", "approve_amount"]
    },
    SchemasTypes.PRODUCT.value: {
        "type": "object",
        "properties": {
            "period": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                }
            },
        },
        "required": ["period"]
    },

    SchemasTypes.CONTACT.value: {
        "type": "object"
    }
}
