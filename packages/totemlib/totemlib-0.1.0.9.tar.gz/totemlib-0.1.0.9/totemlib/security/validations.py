# Validaciones genéricas estándar
# Creado por: Totem Bear
# Fecha: 05-Sep-2023


def validate_fields(data: dict, rules: dict) -> dict:
    """
    Valida los campos de entrada para asegurarse de que existen y son del tipo 
    y tamaño correcto.
    
    Args:
        data (dict): Diccionario con los datos a validar.
        rules (dict): Diccionario con las reglas de validación. 
            Ejemplo: {'tel_id': {'type': str, 'max_length': 20}, 
                      'latitud': {'type': float}}
            
    Returns:
        dict: Un diccionario que contiene la información sobre la validez de 
            cada campo.
            - "valid": Un booleano que indica si todos los campos son válidos.
            - "errors": Una lista de mensajes de error.
    """
    
    errors = []
    
    for field, rule in rules.items():
        value = data.get(field)
        type_ = rule.get('type')
        max_length = rule.get('max_length')
        
        if value is None:
            errors.append(f"{field} no puede ser None.")
            continue

        if not isinstance(value, type_):
            errors.append(f"{field} debe ser de tipo {type_.__name__}.")
            continue

        if max_length and isinstance(value, str) and len(value) > max_length:
            errors.append(f"{field} no puede tener más de {max_length} "\
                          f"caracteres.")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
