# CLAUDE.md - JYE Barcode System

## 🎯 OBJETIVO DEL PROYECTO

Crear sistema de generación e impresión de códigos de barras internos para Didácticos Jugando y Educando. Los códigos de barras se usan en POS para facturación y en CEDI para gestión de inventario en contenedores.

---

## 📋 CONTEXTO DE NEGOCIO

### Problema
- Mercancía de importación (1,500 refs) + stock actual (8,500 refs) = ~10,000 referencias sin código de barras
- Sistema TBC (ERP) requiere códigos de barras para operación
- No usar GS1/Logyca (empresa B2C, códigos internos suficientes)

### Estructura TBC
- **Comodín**: Identificador de proveedor (3 dígitos máximo)
- **SKU (TBC)**: Identificador único de producto (5 dígitos máximo)
- **Código de Barras**: Concatenación de ambos con padding

### Hardware Disponible
- Impresora: Zebra GC420t (EPL)
- Etiquetas: 5x2.5cm rectangulares en rollo

---

## 🏗️ ARQUITECTURA TÉCNICA

### Stack
- **Frontend**: Python + Streamlit Cloud
- **Backend/DB**: Supabase (proyecto nuevo)
- **Impresión**: Generación de archivos EPL para descarga

### Formato de Código de Barras
```
[3 dígitos comodín] + [5 dígitos SKU] = 8 dígitos totales

Ejemplos:
- Comodín 385, SKU 98778 → 38598778
- Comodín 52, SKU 1234   → 05201234
- Comodín 8, SKU 99      → 00800099
```

**Validaciones:**
- Comodín: máximo 3 dígitos, solo numérico
- SKU: máximo 5 dígitos, solo numérico
- Padding automático: `comodin.zfill(3) + sku.zfill(5)`

---

## 🗄️ SCHEMA SUPABASE

### Tabla: `codigos_barras`

```sql
CREATE TABLE codigos_barras (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_barras TEXT UNIQUE NOT NULL,
  comodin_proveedor TEXT NOT NULL,
  tbc_sku TEXT NOT NULL,
  fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  impreso BOOLEAN DEFAULT FALSE,
  fecha_impresion TIMESTAMP WITH TIME ZONE,
  
  CONSTRAINT unique_comodin_sku UNIQUE (comodin_proveedor, tbc_sku),
  CONSTRAINT check_codigo_length CHECK (length(codigo_barras) = 8),
  CONSTRAINT check_codigo_numeric CHECK (codigo_barras ~ '^[0-9]{8}$'),
  CONSTRAINT check_comodin_length CHECK (length(comodin_proveedor) <= 3),
  CONSTRAINT check_sku_length CHECK (length(tbc_sku) <= 5)
);

-- Índices para performance
CREATE INDEX idx_codigo_barras ON codigos_barras(codigo_barras);
CREATE INDEX idx_tbc_sku ON codigos_barras(tbc_sku);
CREATE INDEX idx_comodin ON codigos_barras(comodin_proveedor);
CREATE INDEX idx_impreso ON codigos_barras(impreso);
CREATE INDEX idx_fecha_creacion ON codigos_barras(fecha_creacion);
```

---

## 🎨 FUNCIONALIDADES MVP

### TAB 1: Generación Individual
**Input:**
- Comodín (text input, max 3 dígitos)
- TBC SKU (text input, max 5 dígitos)
- Cantidad de copias (number input, 1-100, default 1)

**Validaciones:**
- Campos no vacíos
- Solo números
- Longitud máxima
- Código no existe en Supabase

**Output:**
- Crea registro en Supabase
- Genera archivo EPL
- Botón de descarga: `{codigo_barras}.epl`
- Mensaje de éxito con código generado

**Flujo:**
```python
1. Usuario ingresa: comodín=385, sku=98778, copias=5
2. Sistema valida inputs
3. Genera código: 38598778
4. Verifica unicidad en Supabase
5. Inserta registro (impreso=False)
6. Genera EPL con 5 copias
7. Botón de descarga aparece
```

### TAB 2: Impresión Masiva
**Filtros:**
- Comodín (dropdown con opciones únicas de DB + "Todos")
- Estado: Impresos / No Impresos / Todos
- Rango de fechas (opcional)

**Lista de Códigos:**
- Checkbox por código
- Muestra: codigo_barras | TBC_SKU | comodín
- Number input "Copias" (solo visible si checkbox activo)

**Footer:**
- Preview: "Total: X códigos seleccionados, Y etiquetas"
- Botón: "📥 Descargar lote completo"

**Output:**
- Un solo archivo EPL con todos los códigos
- Nombre: `lote_{timestamp}.epl`
- Actualiza `impreso=True` y `fecha_impresion` para códigos seleccionados

**Flujo:**
```python
1. Usuario filtra por comodín=385, no impresos
2. Aparecen 10 códigos
3. Selecciona 3 códigos: 5 copias, 10 copias, 30 copias
4. Preview: "3 códigos, 45 etiquetas"
5. Click "Descargar lote"
6. Genera EPL único con los 3 códigos
7. Actualiza DB (impreso=True para esos 3)
8. Descarga archivo
```

### TAB 3: Búsqueda y Consulta
**Funcionalidad:**
- Input: Buscar por código de barras o TBC_SKU
- Muestra detalles del código
- Opción "Reimprimir" (genera EPL nuevamente sin cambiar estado)
- Cantidad de copias para reimpresión

---

## 📄 FORMATO EPL

### Estructura del Archivo

```epl
N
q406
Q203,26
B100,50,0,1,2,4,60,N,"{codigo_barras}"
A100,150,0,3,1,1,N,"{codigo_barras}"
P{cantidad}
```

**Explicación de comandos:**
- `N`: Limpiar buffer
- `q406`: Ancho etiqueta (5cm = 406 dots a 203dpi)
- `Q203,26`: Alto etiqueta (2.5cm = 203 dots) + gap 26
- `B100,50...`: Barcode Code 128, posición (100,50)
- `A100,150...`: Texto legible, posición (100,150)
- `P{cantidad}`: Imprimir N copias

### EPL para Lote (múltiples códigos)

```epl
N
q406
Q203,26
B100,50,0,1,2,4,60,N,"38598778"
A100,150,0,3,1,1,N,"38598778"
P5

N
q406
Q203,26
B100,50,0,1,2,4,60,N,"05201234"
A100,150,0,3,1,1,N,"05201234"
P10

N
q406
Q203,26
B100,50,0,1,2,4,60,N,"00800099"
A100,150,0,3,1,1,N,"00800099"
P30
```

---

## 🔧 LIBRERÍAS PYTHON

```
streamlit
supabase
python-barcode  # Para validación/preview (opcional)
Pillow          # Si necesitas preview visual
python-dotenv   # Para secrets
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
jye-barcode-system/
├── .streamlit/
│   └── secrets.toml
├── app.py                 # Main Streamlit app
├── database.py           # Supabase client y funciones
├── barcode_generator.py  # Lógica de generación de códigos
├── epl_generator.py      # Generación de archivos EPL
├── requirements.txt
└── README.md
```

---

## 🚀 COMANDOS INCREMENTALES PARA CLAUDE CODE

### COMANDO 1: Setup del Proyecto
```
Crea la estructura base del proyecto:
- Carpetas y archivos principales
- requirements.txt con dependencias
- .gitignore
- README.md con instrucciones de setup
- .streamlit/secrets.toml.example (template sin credentials)
```

### COMANDO 2: Database Module
```
Crea database.py con:
- Cliente de Supabase (usando secrets)
- Función: crear_codigo_barras(comodin, sku) → dict
- Función: verificar_codigo_existe(codigo_barras) → bool
- Función: obtener_codigos(filtros: dict) → list
- Función: actualizar_estado_impreso(codigo_ids: list) → bool
- Función: buscar_codigo(query: str) → dict or None
- Función: obtener_comodines_unicos() → list
- Manejo de errores con try/except
```

### COMANDO 3: Barcode Generator Module
```
Crea barcode_generator.py con:
- Función: generar_codigo(comodin: str, sku: str) → str
  - Valida inputs (longitud, solo numérico)
  - Aplica padding con zfill
  - Retorna código de 8 dígitos
- Función: validar_inputs(comodin: str, sku: str) → tuple[bool, str]
  - Retorna (es_valido, mensaje_error)
- Constantes: MAX_COMODIN_LENGTH = 3, MAX_SKU_LENGTH = 5
```

### COMANDO 4: EPL Generator Module
```
Crea epl_generator.py con:
- Función: generar_epl_individual(codigo_barras: str, cantidad: int) → str
  - Retorna contenido EPL como string
- Función: generar_epl_batch(codigos_y_cantidades: list[tuple]) → str
  - Recibe [(codigo1, cant1), (codigo2, cant2), ...]
  - Retorna EPL concatenado con todos los códigos
- Template EPL con comandos correctos para Zebra GC420t
```

### COMANDO 5: Streamlit App - Estructura Base
```
Crea app.py con:
- Imports necesarios
- Configuración de página (título, icon, layout wide)
- Sidebar con logo/título de la empresa
- Inicialización de cliente Supabase
- Estructura de tabs: st.tabs(["Generación Individual", "Impresión Masiva", "Búsqueda"])
- Placeholders para cada tab
```

### COMANDO 6: TAB 1 - Generación Individual
```
Implementa TAB 1 en app.py:
- Form con inputs: comodín, sku, cantidad
- Validación en tiempo real
- Botón "Generar Código"
- Lógica:
  1. Validar inputs
  2. Generar código
  3. Verificar unicidad en DB
  4. Crear registro en Supabase
  5. Generar EPL
  6. Mostrar botón de descarga
- Mensajes de éxito/error con st.success/st.error
- Instrucciones de impresión (info box)
```

### COMANDO 7: TAB 2 - Impresión Masiva (Parte 1: Filtros)
```
Implementa filtros en TAB 2:
- Selectbox: Comodín (dropdown dinámico desde DB + opción "Todos")
- Radio buttons: Estado (Impresos/No Impresos/Todos)
- Date inputs: Rango de fechas (opcional, con checkbox "Usar filtro de fecha")
- Botón "Aplicar Filtros"
- Lógica: Query a Supabase con filtros aplicados
- Mostrar cantidad de resultados
```

### COMANDO 8: TAB 2 - Impresión Masiva (Parte 2: Lista y Selección)
```
Implementa lista de códigos en TAB 2:
- Iterar sobre resultados filtrados
- Por cada código mostrar: checkbox | codigo_barras | TBC_SKU | comodín
- Si checkbox activo, mostrar number_input para cantidad
- Usar st.session_state para mantener selección
- Footer con preview: "Total: X códigos, Y etiquetas"
```

### COMANDO 9: TAB 2 - Impresión Masiva (Parte 3: Descarga Lote)
```
Implementa descarga batch en TAB 2:
- Botón "Descargar lote completo" (disabled si no hay selección)
- Al hacer click:
  1. Recopilar códigos seleccionados con cantidades
  2. Generar EPL batch
  3. Actualizar estado impreso en DB
  4. Mostrar botón de descarga con nombre lote_{timestamp}.epl
- Mensaje de confirmación
- Opción de limpiar selección después
```

### COMANDO 10: TAB 3 - Búsqueda y Reimpresión
```
Implementa TAB 3:
- Input: Buscar por código de barras o TBC_SKU
- Botón "Buscar"
- Lógica: Query a Supabase
- Si encuentra:
  - Mostrar card con detalles (código, comodín, SKU, fecha creación, impreso)
  - Number input: Cantidad de copias para reimpresión
  - Botón "Reimprimir" (genera EPL sin cambiar estado)
- Si no encuentra: mensaje "Código no encontrado"
```

### COMANDO 11: Testing y Refinamiento
```
Prueba y ajusta:
- Mensajes de error claros y específicos
- Validación de edge cases (campos vacíos, caracteres especiales)
- UX: loading spinners en operaciones de DB
- Confirmación antes de operaciones masivas
- Responsive: que funcione bien en diferentes tamaños de pantalla
```

### COMANDO 12: Documentación Final
```
Actualiza README.md con:
- Descripción del proyecto
- Setup instructions:
  1. Clonar repo
  2. Instalar dependencias
  3. Configurar Supabase (crear tabla, obtener URL y key)
  4. Configurar secrets.toml
  5. Correr app
- Guía de uso de cada tab
- Troubleshooting común
- Flujo de impresión (Zebra Setup Utilities)
```

---

## 🔐 SECRETS (Supabase)

```toml
# .streamlit/secrets.toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "tu-anon-key"
```

---

## ✅ CRITERIOS DE ÉXITO

- [ ] Usuario puede crear código individual con comodín + SKU
- [ ] Sistema valida inputs y previene duplicados
- [ ] Genera archivos EPL descargables
- [ ] Impresión masiva con selección múltiple y cantidades variables
- [ ] Filtros funcionales (comodín, estado, fechas)
- [ ] Búsqueda por código o SKU con reimpresión
- [ ] DB actualiza correctamente estado de impresión
- [ ] Archivos EPL imprimen correctamente en Zebra GC420t
- [ ] UI intuitiva y sin pasos innecesarios

---

## 📝 NOTAS ADICIONALES

### Flujo de Impresión (Usuario Final)
1. Descargar archivo `.epl` desde Streamlit
2. Abrir **Zebra Setup Utilities**
3. Click derecho en impresora GC420t
4. "Send File" → Seleccionar archivo descargado
5. Etiquetas se imprimen automáticamente

### Futuras Mejoras (Post-MVP)
- Upload CSV para carga masiva (cuando llegue importación grande)
- Estadísticas y dashboard (códigos por proveedor, tendencias)
- Exportar reporte de códigos generados
- Integración API directa con TBC (si es posible)

---

**PROYECTO LISTO PARA CLAUDE CODE** 🚀

Procede comando por comando, validando con Antigravity cada 2-3 comandos.
