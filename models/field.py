from datetime import datetime

class Field:
    def __init__(self, identifier, field_type, position, label, options=None):
        if field_type in ["Select", "Radio"] and not options:
            options = [
                {"text": "Opção 1", "value": "opcao1"},
                {"text": "Opção 2", "value": "opcao2"}
            ]
        self.data = {
            "position": position,
            "identifier": identifier,
            "label": label,
            "type": field_type,
            "required": True,
            "defaultValue": "",
            "group": None,
            "size": {"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6},
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "suspended": False,
            "disabled": False,
            "visible": True,
            "protected": False,
            "options": options,
            "helpText": None,
            "error": None
        }

    def to_dict(self):
        return self.data

def create_field(identifier, field_type, position, label, options=None):
    return Field(identifier, field_type, position, label, options).to_dict()

# Função para normalizar tipos de campo
def normalize_type(t):
    ALLOWED_TYPES = ["LineText", "TextArea", "Number", "Select", "Checkbox", "Radio", "Toggle", "Date"]
    t = t.strip()
    return t if t in ALLOWED_TYPES else "LineText"