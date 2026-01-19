# JYE Barcode System

Sistema de generación e impresión de códigos de barras internos para **Didácticos Jugando y Educando**.

![Version](https://img.shields.io/badge/version-1.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red)

---

## Descripción

Sistema web desarrollado con Streamlit para generar y gestionar códigos de barras internos de 8 dígitos. Los códigos se utilizan en puntos de venta (POS) para facturación y en el CEDI para gestión de inventario en contenedores.

**Formato del código:** `[3 dígitos comodín] + [5 dígitos SKU] = 8 dígitos totales`

**Ejemplos:**
- Comodín `385` + SKU `98778` → `38598778`
- Comodín `52` + SKU `1234` → `05201234`
- Comodín `8` + SKU `99` → `00800099`

### Características principales

- **Generación Individual**: Crea códigos nuevos con validación de unicidad
- **Impresión Masiva**: Filtra, selecciona y genera lotes de múltiples códigos
- **Búsqueda y Consulta**: Busca códigos existentes por código completo o SKU
- **Reimpresión**: Genera archivos EPL sin modificar estado en BD
- **Gestión de Estado**: Actualiza automáticamente el estado de impresión
- **Validaciones Robustas**: Previene duplicados y valida inputs
- **Base de Datos**: Almacenamiento en Supabase (PostgreSQL)

---

## Requisitos

### Software
- Python 3.8 o superior
- Cuenta en [Supabase](https://supabase.com) (gratuita)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

### Hardware (para impresión)
- Impresora Zebra GC420t (EPL)
- Zebra Setup Utilities instalado
- Etiquetas rectangulares 5x2.5cm en rollo
- Conexión USB entre computadora e impresora

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd codigos_barras_zebra
```

### 2. Crear entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `streamlit>=1.31.0` - Framework web
- `supabase>=2.3.0` - Cliente de base de datos
- `python-barcode>=0.15.1` - Generación de códigos (opcional)
- `Pillow>=10.2.0` - Procesamiento de imágenes (opcional)
- `python-dotenv>=1.0.0` - Gestión de variables de entorno

### 4. Configurar Supabase

#### 4.1 Crear proyecto
1. Ingresa a [Supabase](https://supabase.com) y crea una cuenta
2. Crea un nuevo proyecto
3. Espera a que el proyecto se inicialice (~2 minutos)

#### 4.2 Crear tabla
1. Ve a **SQL Editor** en el panel izquierdo
2. Haz clic en **+ New query**
3. Copia y pega el siguiente SQL:

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

CREATE INDEX idx_codigo_barras ON codigos_barras(codigo_barras);
CREATE INDEX idx_tbc_sku ON codigos_barras(tbc_sku);
CREATE INDEX idx_comodin ON codigos_barras(comodin_proveedor);
CREATE INDEX idx_impreso ON codigos_barras(impreso);
CREATE INDEX idx_fecha_creacion ON codigos_barras(fecha_creacion);
```

4. Haz clic en **Run** (o presiona Ctrl+Enter)
5. Verifica que aparezca el mensaje "Success. No rows returned"

#### 4.3 Obtener credenciales
1. Ve a **Settings** > **API** en el panel izquierdo
2. Copia los siguientes valores:
   - **Project URL**: `https://tu-proyecto.supabase.co`
   - **anon/public key**: Clave larga que empieza con `eyJ...`

### 5. Configurar secrets

#### 5.1 Copiar template
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

#### 5.2 Editar credenciales
Abre `.streamlit/secrets.toml` en un editor de texto y reemplaza con tus credenciales:

```toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**IMPORTANTE:**
- No compartas este archivo
- No lo subas a GitHub o control de versiones
- El archivo `.gitignore` ya lo excluye automáticamente

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

Si no se abre automáticamente, abre tu navegador y visita la URL.

---

## Guía de Uso

### TAB 1: Generación Individual

Genera códigos de barras nuevos uno a la vez.

#### Flujo de trabajo:

1. **Ingresar Comodín Proveedor**
   - Campo: Máximo 3 dígitos numéricos
   - Ejemplo: `385`, `52`, `8`
   - Padding automático: `8` se convierte en `008`

2. **Ingresar TBC SKU**
   - Campo: Máximo 5 dígitos numéricos
   - Ejemplo: `98778`, `1234`, `99`
   - Padding automático: `99` se convierte en `00099`

3. **Definir cantidad de copias**
   - Rango: 1-100 etiquetas
   - Default: 1
   - Warning automático si > 50

4. **Generar código**
   - Click en "Generar Código de Barras"
   - Sistema valida inputs
   - Verifica que el código no exista
   - Crea registro en BD (estado: `impreso=False`)

5. **Descargar archivo**
   - Botón de descarga aparece al generar exitosamente
   - Archivo: `{codigo_barras}.epl` (ej: `38598778.epl`)
   - Listo para enviar a impresora

#### Validaciones:
- ✓ Campos no vacíos
- ✓ Solo números (sin letras ni símbolos)
- ✓ Longitud máxima (3 y 5 dígitos)
- ✓ Código no existe en BD

#### Errores comunes:
- **"El código ya existe"**: El comodín+SKU ya fueron usados. Usa TAB 3 para reimprimir.
- **"Campo vacío"**: Completa todos los campos obligatorios.
- **"Solo números"**: Elimina letras o caracteres especiales.

---

### TAB 2: Impresión Masiva

Filtra, selecciona y genera lotes de múltiples códigos.

#### Paso 1: Aplicar Filtros

**Filtro por Comodín:**
- Dropdown con comodines existentes en BD
- Opción "Todos" para no filtrar

**Filtro por Estado:**
- **Todos**: Muestra impresos y no impresos
- **No Impresos**: Solo códigos con `impreso=False`
- **Impresos**: Solo códigos con `impreso=True`

**Filtro por Fechas (opcional):**
- Activa checkbox "Usar filtro de fecha"
- Define rango: Fecha desde / Fecha hasta
- Validación: `fecha_hasta >= fecha_desde`

**Aplicar:**
- Click en "Aplicar Filtros"
- Sistema muestra cantidad de códigos encontrados

#### Paso 2: Seleccionar Códigos

**Lista de códigos:**
- Checkbox por cada código
- Columnas: Código | SKU | Comodín | Copias

**Definir cantidades:**
- Input de cantidad aparece al activar checkbox
- Rango: 1-100 copias por código
- Cada código puede tener cantidad diferente

**Límite de visualización:**
- Máximo 50 códigos mostrados
- Si hay más, aparece warning
- Usa filtros más específicos

#### Paso 3: Generar Lote

**Preview:**
- Métricas: Códigos seleccionados / Total de etiquetas
- Resumen: "Se generarán X etiquetas de Y códigos"
- Warning si > 50 etiquetas

**Confirmación:**
- Checkbox obligatorio antes de generar
- Texto: "Confirmo que deseo generar X etiquetas..."
- Botón deshabilitado hasta confirmar

**Descargar:**
- Click en "Descargar lote completo"
- Archivo: `lote_YYYYMMDD_HHMMSS.epl`
- Sistema actualiza `impreso=True` en BD
- Botón "Limpiar selección" para reiniciar

#### Ejemplo:

```
Filtros aplicados:
  - Comodín: 385
  - Estado: No Impresos
  - Fechas: 01/01/2026 - 31/01/2026

Resultados: 10 códigos

Selección:
  [✓] 38598778 - SKU 98778 - Comodín 385 → 5 copias
  [✓] 38512345 - SKU 12345 - Comodín 385 → 10 copias
  [✓] 38500099 - SKU 00099 - Comodín 385 → 30 copias

Preview:
  - Códigos Seleccionados: 3
  - Total de Etiquetas: 45

Resultado:
  - Archivo: lote_20260118_235900.epl
  - Códigos actualizados: impreso=True
```

---

### TAB 3: Búsqueda y Consulta

Busca códigos existentes y reimprime sin modificar estado en BD.

#### Buscar:

1. **Ingresar búsqueda**
   - Por código completo: `38598778`
   - Por SKU: `98778`
   - Solo números, máximo 8 dígitos

2. **Click en "Buscar"**
   - Sistema busca en BD
   - Primero busca por código completo
   - Si no encuentra, busca por SKU

#### Ver Detalles:

**Card de información:**
- Código de Barras: `38598778`
- Comodín: `385`
- TBC SKU: `98778`
- Estado: ✅ Impreso / ⚠️ No Impreso
- Fecha de Creación: `18/01/2026 23:30:45`
- Última Impresión: `18/01/2026 23:45:12` (o "Nunca impreso")

#### Reimprimir:

1. **Definir cantidad de copias**
   - Number input: 1-100
   - Default: 1

2. **Click en "Reimprimir Código"**
   - Genera archivo EPL
   - **NO modifica estado en BD** (característica clave)
   - Útil para etiquetas dañadas o perdidas

3. **Descargar**
   - Archivo: `{codigo_barras}.epl`
   - Listo para enviar a impresora

#### Diferencias con TAB 1:

| TAB 1: Generación Individual | TAB 3: Reimpresión |
|------------------------------|-------------------|
| Crea código nuevo | Busca código existente |
| Inserta en BD | No modifica BD |
| `impreso=False` inicial | Estado no cambia |
| Error si duplicado | Permite reimprimir |

---

## Flujo de Impresión con Zebra GC420t

### Configuración inicial (una sola vez):

1. **Instalar Zebra Setup Utilities**
   - Descarga desde [Zebra.com](https://www.zebra.com/us/en/support-downloads.html)
   - Instala siguiendo el asistente
   - Conecta la impresora por USB

2. **Configurar impresora**
   - Abre Zebra Setup Utilities
   - La impresora debe aparecer automáticamente
   - Verifica que esté en modo EPL (no ZPL)

3. **Cargar etiquetas**
   - Usa etiquetas 5x2.5cm rectangulares
   - Carga en el rollo de la impresora
   - Calibra si es necesario (botón Feed)

### Proceso de impresión (cada vez):

1. **Generar archivo en la aplicación**
   - Cualquier tab (1, 2 o 3)
   - Descarga archivo `.epl`

2. **Enviar a impresora**
   - Abre Zebra Setup Utilities
   - Haz clic derecho en "GC420t"
   - Selecciona **"Send File"**
   - Navega y selecciona archivo `.epl` descargado
   - Haz clic en **"Enviar"** o **"Open"**

3. **Imprimir**
   - Las etiquetas se imprimen automáticamente
   - Verifica calidad de impresión
   - Ajusta densidad si es necesario (botones en impresora)

### Tips de impresión:

- **Impresión borrosa**: Aumenta densidad (botón +)
- **Impresión muy oscura**: Disminuye densidad (botón -)
- **Etiquetas saltadas**: Recalibra (mantén botón Feed)
- **No imprime**: Verifica papel, conexión USB, modo EPL

---

## Estructura del Proyecto

```
codigos_barras_zebra/
│
├── .streamlit/
│   ├── secrets.toml          # Credenciales Supabase (NO subir a git)
│   └── secrets.toml.example  # Template de configuración
│
├── app.py                    # Aplicación principal Streamlit (634 líneas)
│   ├── TAB 1: Generación Individual
│   ├── TAB 2: Impresión Masiva
│   └── TAB 3: Búsqueda y Consulta
│
├── database.py               # Módulo de Supabase (200+ líneas)
│   ├── get_supabase_client()
│   ├── crear_codigo_barras()
│   ├── verificar_codigo_existe()
│   ├── obtener_codigos()
│   ├── actualizar_estado_impreso()
│   ├── buscar_codigo()
│   └── obtener_comodines_unicos()
│
├── barcode_generator.py      # Lógica de generación (100+ líneas)
│   ├── validar_inputs()
│   └── generar_codigo()
│
├── epl_generator.py          # Generación de EPL (90+ líneas)
│   ├── generar_epl_individual()
│   ├── generar_epl_batch()
│   └── validar_cantidad()
│
├── requirements.txt          # Dependencias Python
├── .gitignore               # Exclusiones de Git
├── CLAUDE.md                # Especificaciones técnicas
└── README.md                # Este archivo
```

---

## Troubleshooting

### Problemas de Conexión

#### Error: "Error al conectar con la base de datos"

**Causas posibles:**
1. Credenciales incorrectas en `secrets.toml`
2. Sin conexión a internet
3. Proyecto de Supabase pausado o eliminado
4. URL o key con espacios o caracteres extra

**Soluciones:**
1. Verifica credenciales:
   ```toml
   # Correcto (sin espacios)
   url = "https://proyecto.supabase.co"

   # Incorrecto (con salto de línea)
   url = "https://proyecto.supabase.co
   "
   ```

2. Verifica conexión a internet
3. Ingresa a Supabase y verifica que el proyecto esté activo
4. Regenera las credenciales si es necesario

#### Error: "Table 'codigos_barras' does not exist"

**Causa:** La tabla no fue creada en Supabase

**Solución:**
1. Ingresa a Supabase > SQL Editor
2. Ejecuta el script SQL de la sección 4.2
3. Verifica en "Table Editor" que la tabla exista

---

### Problemas con Códigos

#### Error: "El código de barras ya existe"

**Causa:** Intentas crear un código con comodín+SKU ya usado

**Soluciones:**
1. **Si necesitas reimprimir**: Usa TAB 3 (Búsqueda)
2. **Si es error**: Verifica comodín y SKU ingresados
3. **Si quieres cambiar**: Modifica comodín o SKU

**Ejemplo:**
```
❌ Intentaste: Comodín 385 + SKU 98778
✓ Ya existe en BD
✓ Solución: TAB 3 → Buscar "38598778" → Reimprimir
```

#### Error: "Solo debe contener números"

**Causa:** Input con letras, espacios o símbolos

**Solución:** Elimina todo excepto números
```
❌ Incorrecto: "385A", "38 5", "385-"
✓ Correcto: "385"
```

#### Error: "No se encontró ningún código"

**Causa:** El código no existe en BD o búsqueda incorrecta

**Soluciones:**
1. Verifica que escribiste correctamente
2. Busca solo con números
3. Intenta buscar solo con SKU
4. Verifica en TAB 2 si el código existe

---

### Problemas de Impresión

#### La impresora no imprime

**Checklist:**
- [ ] Impresora encendida (luz verde)
- [ ] Cable USB conectado
- [ ] Etiquetas cargadas correctamente
- [ ] Zebra Setup Utilities instalado
- [ ] Impresora visible en Zebra Setup Utilities
- [ ] Modo EPL activado (no ZPL)
- [ ] Archivo `.epl` válido (descargado desde app)

**Pasos de diagnóstico:**
1. Abre Zebra Setup Utilities
2. Verifica que la impresora aparezca
3. Haz clic derecho > "Print Configuration Label"
4. Si imprime etiqueta de configuración, el hardware funciona
5. Si no imprime nada, revisa conexión USB y drivers

#### Impresión con calidad baja

**Síntomas y soluciones:**

| Síntoma | Causa | Solución |
|---------|-------|----------|
| Código borroso | Densidad baja | Presiona botón `+` en impresora |
| Código muy oscuro | Densidad alta | Presiona botón `-` en impresora |
| Barras cortadas | Etiquetas mal calibradas | Mantén botón `Feed` 3 segundos |
| Posición incorrecta | Configuración de tamaño | Verifica etiquetas 5x2.5cm |
| No escanea | Código muy claro/oscuro | Ajusta densidad |

#### Error: "Archivo EPL inválido"

**Causa:** Archivo modificado manualmente o corrupto

**Solución:**
1. NO edites archivos `.epl` manualmente
2. Regenera desde la aplicación
3. Descarga nuevamente
4. Si persiste, reporta bug

---

### Problemas de Rendimiento

#### TAB 2 lento con muchos códigos

**Causa:** Más de 50 códigos en lista

**Solución:**
- Usa filtros más específicos
- Filtra por comodín específico
- Filtra por estado (No Impresos)
- Usa rango de fechas corto

**Ejemplo:**
```
❌ Lento: Filtro "Todos" → 500 códigos
✓ Rápido: Filtro "Comodín 385" → 20 códigos
```

#### Base de datos lenta

**Causa:** Muchos registros sin índices o plan gratuito

**Solución:**
1. Verifica que los índices estén creados (script SQL los crea)
2. Considera plan de pago si > 10,000 códigos
3. Limpia códigos antiguos si es necesario

---

## Mejores Prácticas

### Gestión de Códigos

1. **Asigna comodines por proveedor**
   ```
   Proveedor A → Comodín 100-199
   Proveedor B → Comodín 200-299
   Proveedor C → Comodín 300-399
   ```

2. **Usa SKUs secuenciales por categoría**
   ```
   Juguetes → SKU 1-9999
   Libros → SKU 10000-19999
   Papelería → SKU 20000-29999
   ```

3. **Reimprimir en lugar de regenerar**
   - Si perdiste una etiqueta, usa TAB 3
   - No crees códigos duplicados

### Gestión de Etiquetas

1. **Imprime en lotes de 20-30** para mejor eficiencia
2. **Verifica calidad** en primera etiqueta antes de imprimir todo
3. **Mantén stock** de etiquetas (mínimo 1 rollo de repuesto)
4. **Archiva archivos EPL** de lotes grandes por 30 días

### Base de Datos

1. **Backup periódico** (Supabase lo hace automático)
2. **Monitorea uso** en panel de Supabase
3. **No elimines registros** sin respaldo
4. **Usa filtros** para optimizar queries

---

## Preguntas Frecuentes (FAQ)

**¿Puedo usar otros tamaños de etiqueta?**
Sí, pero debes modificar el archivo `epl_generator.py` con las dimensiones correctas en dots (dpi).

**¿Funciona con otras impresoras Zebra?**
Sí, cualquier impresora Zebra compatible con EPL debería funcionar. Verifica la resolución (203 dpi).

**¿Puedo importar códigos existentes en masa?**
No está implementado en MVP. Puedes agregar esta funcionalidad modificando el código.

**¿Los códigos cumplen con estándares GS1?**
No, son códigos internos. Para distribución externa usa GS1/Logyca.

**¿Puedo cambiar el formato de 8 dígitos?**
Sí, pero requiere modificar `barcode_generator.py` y el schema de Supabase.

**¿Funciona offline?**
No, requiere conexión a internet para acceder a Supabase.

**¿Puedo tener múltiples usuarios?**
Sí, todos con acceso a `secrets.toml` pueden usar el sistema simultáneamente.

**¿Los códigos tienen checksum?**
No en el MVP. Code 128 incluye checksum automático en el barcode.

---

## Tecnologías

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Frontend | Streamlit | 1.31+ |
| Backend | Supabase | Cloud |
| Base de Datos | PostgreSQL | 15+ |
| Lenguaje | Python | 3.8+ |
| Impresión | EPL | 2 |
| Hardware | Zebra GC420t | EPL Mode |

---

## Licencia

Proyecto privado para uso interno de **Didácticos Jugando y Educando**.

---

## Soporte y Contacto

- **Documentación técnica**: Ver archivo `CLAUDE.md`
- **Reportar bugs**: Contacta al administrador del sistema
- **Mejoras**: Sugiere funcionalidades al equipo de TI

---

## Changelog

### v1.0.1 (2026-01-19)
- 🔧 **FIX CRÍTICO**: Corregido template EPL - removidas comillas en códigos de barras
- ✅ Template EPL ahora imprime correctamente (antes se imprimía como texto plano)
- 📝 Formato correcto: `B100,50,0,1,2,4,60,N,{codigo}` (sin comillas)

### v1.0.0 (2026-01-18)
- ✅ Generación individual de códigos
- ✅ Impresión masiva con filtros
- ✅ Búsqueda y reimpresión
- ✅ Validaciones completas
- ✅ Confirmaciones para operaciones masivas
- ✅ Gestión de estado en BD
- ✅ Archivos EPL para Zebra GC420t

---

**¡Sistema listo para producción!** 🚀

Para comenzar, ejecuta: `streamlit run app.py`
