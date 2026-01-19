# COMANDO: Convertir de EPL a ZPL

## Contexto
La impresora Zebra GC420t está configurada en modo ZPL (no EPL). Actualmente los archivos .epl se están imprimiendo como texto plano en vez de ejecutar los comandos. Necesitamos cambiar el generador para que use ZPL en vez de EPL.

## Instrucción

La impresora Zebra GC420t está configurada en modo ZPL (no EPL). Necesito que modifiques el archivo `epl_generator.py` para generar comandos ZPL en vez de EPL.

### FORMATO ZPL REQUERIDO:
- Tamaño etiqueta: 5cm x 2.5cm (406x203 dots a 203dpi)
- Código de barras Code 128
- Texto legible debajo del código

### TEMPLATE ZPL PARA CÓDIGO INDIVIDUAL:

```zpl
^XA
^FO100,30
^BY2
^BCN,80,Y,N,N
^FD{codigo_barras}^FS
^FO100,130
^A0N,25,25
^FD{codigo_barras}^FS
^PQ{cantidad}
^XZ
```

### TEMPLATE ZPL PARA BATCH (múltiples códigos):

Para múltiples códigos, concatenar múltiples bloques ^XA...^XZ, uno por cada código:

```zpl
^XA
^FO100,30
^BY2
^BCN,80,Y,N,N
^FD38598778^FS
^FO100,130
^A0N,25,25
^FD38598778^FS
^PQ5
^XZ

^XA
^FO100,30
^BY2
^BCN,80,Y,N,N
^FD05201234^FS
^FO100,130
^A0N,25,25
^FD05201234^FS
^PQ10
^XZ
```

### CAMBIOS A REALIZAR:

1. **Renombrar archivo**: `epl_generator.py` → `zpl_generator.py`

2. **Actualizar funciones**:
   - `generar_epl_individual()` → `generar_zpl_individual()`
   - `generar_epl_batch()` → `generar_zpl_batch()`

3. **Actualizar app.py**:
   - Cambiar import: `from epl_generator import` → `from zpl_generator import`
   - Cambiar extensión de archivos descargables: `.epl` → `.zpl`
   - Actualizar todos los nombres de funciones que llamen a los generadores

4. **Actualizar README.md**:
   - Cambiar todas las referencias de EPL a ZPL
   - Actualizar ejemplos de impresión con extensión .zpl

### EXPLICACIÓN DE COMANDOS ZPL:

- `^XA` = Inicio de formato
- `^FO100,30` = Posición del barcode (x=100, y=30)
- `^BY2` = Ancho de barra
- `^BCN,80,Y,N,N` = Barcode Code 128, altura 80, imprimir número arriba=Y
- `^FD{codigo}^FS` = Field Data con el código
- `^FO100,130` = Posición del texto legible
- `^A0N,25,25` = Font size 25x25
- `^PQ{cantidad}` = Print Quantity (número de copias)
- `^XZ` = Fin de formato

### IMPORTANTE:
- Mantener todas las funcionalidades existentes
- Solo cambiar el formato de comandos de EPL a ZPL
- No cambiar la lógica de validación o base de datos
- Asegurar que la función batch siga generando un solo archivo con múltiples bloques ^XA...^XZ
