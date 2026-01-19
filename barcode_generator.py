"""
Barcode Generator Module for JYE Barcode System
Handles barcode generation and input validation
"""

from typing import Tuple

# Constantes de validación
MAX_COMODIN_LENGTH = 3
MAX_SKU_LENGTH = 5


def validar_inputs(comodin: str, sku: str) -> Tuple[bool, str]:
    """
    Valida los inputs de comodín y SKU

    Args:
        comodin: Código comodín del proveedor
        sku: SKU TBC

    Returns:
        tuple: (es_valido, mensaje_error)
            - es_valido: True si todos los inputs son válidos, False si hay error
            - mensaje_error: Descripción del error o string vacío si es válido
    """
    # Validar que los campos no estén vacíos
    if not comodin or not comodin.strip():
        return False, "El campo Comodín no puede estar vacío"

    if not sku or not sku.strip():
        return False, "El campo TBC SKU no puede estar vacío"

    # Limpiar espacios
    comodin = comodin.strip()
    sku = sku.strip()

    # Validar que sean solo numéricos
    if not comodin.isdigit():
        return False, "El Comodín debe contener solo números"

    if not sku.isdigit():
        return False, "El TBC SKU debe contener solo números"

    # Validar longitud máxima
    if len(comodin) > MAX_COMODIN_LENGTH:
        return False, f"El Comodín no puede tener más de {MAX_COMODIN_LENGTH} dígitos"

    if len(sku) > MAX_SKU_LENGTH:
        return False, f"El TBC SKU no puede tener más de {MAX_SKU_LENGTH} dígitos"

    # Validar que no sean cero o negativos (aunque isdigit ya previene negativos)
    if int(comodin) < 0:
        return False, "El Comodín debe ser un número positivo"

    if int(sku) < 0:
        return False, "El TBC SKU debe ser un número positivo"

    return True, ""


def generar_codigo(comodin: str, sku: str) -> str:
    """
    Genera un código de barras de 8 dígitos aplicando padding

    Args:
        comodin: Código comodín del proveedor (será padded a 3 dígitos)
        sku: SKU TBC (será padded a 5 dígitos)

    Returns:
        str: Código de barras de 8 dígitos (formato: XXX + XXXXX)

    Raises:
        ValueError: Si los inputs no son válidos

    Examples:
        >>> generar_codigo("385", "98778")
        '38598778'
        >>> generar_codigo("52", "1234")
        '05201234'
        >>> generar_codigo("8", "99")
        '00800099'
    """
    # Validar inputs
    es_valido, mensaje_error = validar_inputs(comodin, sku)

    if not es_valido:
        raise ValueError(mensaje_error)

    # Limpiar espacios
    comodin = comodin.strip()
    sku = sku.strip()

    # Aplicar padding: 3 dígitos para comodín, 5 para SKU
    codigo_barras = comodin.zfill(MAX_COMODIN_LENGTH) + sku.zfill(MAX_SKU_LENGTH)

    return codigo_barras
