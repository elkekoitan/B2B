from typing import Dict, Any, List


TEMPLATES: Dict[str, Dict[str, Any]] = {
    "chemicals": {
        "category": "chemicals",
        "fields": [
            {"name": "cas_number", "label": "CAS Number", "type": "string", "required": True},
            {"name": "purity", "label": "Purity (%)", "type": "number", "required": True},
            {"name": "msds_required", "label": "MSDS Required", "type": "boolean", "required": True},
            {"name": "packaging", "label": "Packaging", "type": "string", "required": False}
        ],
        "compliance_checklist": [
            "REACH compliance",
            "Hazard labeling",
            "Transport documentation"
        ]
    },
    "electronics": {
        "category": "electronics",
        "fields": [
            {"name": "spec_sheet", "label": "Spec Sheet", "type": "file", "required": True},
            {"name": "certifications", "label": "Certifications", "type": "list", "required": True},
            {"name": "warranty", "label": "Warranty (months)", "type": "number", "required": False}
        ],
        "compliance_checklist": [
            "CE/FCC/RoHS",
            "EMC testing",
            "Warranty terms"
        ]
    },
    "textiles": {
        "category": "textiles",
        "fields": [
            {"name": "material", "label": "Material", "type": "string", "required": True},
            {"name": "gsm", "label": "GSM", "type": "number", "required": True},
            {"name": "color", "label": "Color", "type": "string", "required": False}
        ],
        "compliance_checklist": [
            "Color fastness",
            "Shrinkage tolerance",
            "Fabric composition"
        ]
    }
}


def list_templates() -> List[Dict[str, str]]:
    return [{"category": key, "title": key.title()} for key in TEMPLATES.keys()]


def get_template(category: str) -> Dict[str, Any]:
    key = (category or "").lower()
    if key not in TEMPLATES:
        raise KeyError("Template not found")
    return TEMPLATES[key]

