"""
ZPL Generator Module for JYE Barcode System
Generates ZPL (Zebra Programming Language) files for Zebra GC420t printer
"""

from typing import List, Tuple


def generar_zpl_individual(codigo_barras: str, cantidad: int = 1) -> str:
    """
    Genera contenido ZPL para un código de barras individual

    Args:
        codigo_barras: Código de barras de 8 dígitos a imprimir
        cantidad: Número de copias a imprimir (default: 1)

    Returns:
        str: Contenido del archivo ZPL listo para enviar a la impresora

    Example:
        >>> zpl = generar_zpl_individual("38598778", 5)
        >>> # Genera ZPL para imprimir 5 copias del código 38598778
    """
    # Template ZPL para Zebra GC420t (203 dpi)
    # Etiquetas: 5x2.5cm (406x203 dots a 203dpi)
    zpl_content = f"""^XA
^FO100,30
^BY2
^BCN,80,Y,N,N
^FD{codigo_barras}^FS
^FO100,130
^A0N,25,25
^FD{codigo_barras}^FS
^PQ{cantidad}
^XZ
"""
    return zpl_content


def generar_zpl_batch(codigos_y_cantidades: List[Tuple[str, int]]) -> str:
    """
    Genera contenido ZPL para múltiples códigos de barras en un solo archivo

    Args:
        codigos_y_cantidades: Lista de tuplas (codigo_barras, cantidad)
            Ejemplo: [("38598778", 5), ("05201234", 10), ("00800099", 30)]

    Returns:
        str: Contenido ZPL concatenado con todos los códigos

    Example:
        >>> codigos = [("38598778", 5), ("05201234", 10)]
        >>> zpl = generar_zpl_batch(codigos)
        >>> # Genera ZPL para imprimir múltiples códigos en secuencia
    """
    if not codigos_y_cantidades:
        return ""

    # Generar ZPL para cada código y concatenar
    zpl_blocks = []

    for codigo_barras, cantidad in codigos_y_cantidades:
        zpl_block = f"""^XA
^FO100,30
^BY2
^BCN,80,Y,N,N
^FD{codigo_barras}^FS
^FO100,130
^A0N,25,25
^FD{codigo_barras}^FS
^PQ{cantidad}
^XZ
"""
        zpl_blocks.append(zpl_block)

    # Unir todos los bloques
    zpl_content = "\n".join(zpl_blocks)

    return zpl_content


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
