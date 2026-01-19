"""
EPL Generator Module for JYE Barcode System
Generates EPL (Eltron Programming Language) files for Zebra GC420t printer
"""

from typing import List, Tuple


def generar_epl_individual(codigo_barras: str, cantidad: int = 1) -> str:
    """
    Genera contenido EPL para un código de barras individual

    Args:
        codigo_barras: Código de barras de 8 dígitos a imprimir
        cantidad: Número de copias a imprimir (default: 1)

    Returns:
        str: Contenido del archivo EPL listo para enviar a la impresora

    Example:
        >>> epl = generar_epl_individual("38598778", 5)
        >>> # Genera EPL para imprimir 5 copias del código 38598778
    """
    # Template EPL para Zebra GC420t (203 dpi)
    # Etiquetas: 5x2.5cm (406x203 dots a 203dpi)
    epl_content = f"""N
q406
Q203,26
B100,50,0,1,2,4,60,N,"{codigo_barras}"
A100,150,0,3,1,1,N,"{codigo_barras}"
P{cantidad}
"""
    return epl_content


def generar_epl_batch(codigos_y_cantidades: List[Tuple[str, int]]) -> str:
    """
    Genera contenido EPL para múltiples códigos de barras en un solo archivo

    Args:
        codigos_y_cantidades: Lista de tuplas (codigo_barras, cantidad)
            Ejemplo: [("38598778", 5), ("05201234", 10), ("00800099", 30)]

    Returns:
        str: Contenido EPL concatenado con todos los códigos

    Example:
        >>> codigos = [("38598778", 5), ("05201234", 10)]
        >>> epl = generar_epl_batch(codigos)
        >>> # Genera EPL para imprimir múltiples códigos en secuencia
    """
    if not codigos_y_cantidades:
        return ""

    # Generar EPL para cada código y concatenar
    epl_blocks = []

    for codigo_barras, cantidad in codigos_y_cantidades:
        epl_block = f"""N
q406
Q203,26
B100,50,0,1,2,4,60,N,"{codigo_barras}"
A100,150,0,3,1,1,N,"{codigo_barras}"
P{cantidad}
"""
        epl_blocks.append(epl_block)

    # Unir todos los bloques
    epl_content = "\n".join(epl_blocks)

    return epl_content


def validar_cantidad(cantidad: int, max_cantidad: int = 100) -> Tuple[bool, str]:
    """
    Valida que la cantidad de copias sea válida

    Args:
        cantidad: Número de copias solicitadas
        max_cantidad: Cantidad máxima permitida (default: 100)

    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if cantidad < 1:
        return False, "La cantidad debe ser al menos 1"

    if cantidad > max_cantidad:
        return False, f"La cantidad no puede exceder {max_cantidad} copias"

    return True, ""
