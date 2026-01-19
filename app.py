"""
JYE Barcode System - Sistema de Generación e Impresión de Códigos de Barras
Didácticos Jugando y Educando
"""

import streamlit as st
from datetime import datetime
import database as db
import barcode_generator as bg
import epl_generator as epl

# Configuración de página
st.set_page_config(
    page_title="JYE Barcode System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.title("📦 JYE Barcode System")
    st.markdown("---")
    st.markdown("### Didácticos Jugando y Educando")
    st.markdown("Sistema de generación e impresión de códigos de barras internos")
    st.markdown("---")
    st.markdown("**Formato:** 8 dígitos")
    st.markdown("**Estructura:** [3 comodín] + [5 SKU]")
    st.markdown("**Impresora:** Zebra GC420t (EPL)")
    st.markdown("---")
    st.info("💡 Los archivos .epl se envían a la impresora usando Zebra Setup Utilities")

# Título principal
st.title("Sistema de Códigos de Barras JYE")
st.markdown("Genera e imprime códigos de barras para inventario y facturación")
st.markdown("---")

# Inicializar cliente Supabase (verificar conexión)
try:
    supabase_client = db.get_supabase_client()
    # st.success("✅ Conectado a base de datos")
except Exception as e:
    st.error(f"❌ Error al conectar con la base de datos")
    st.error(f"**Detalles:** {str(e)}")
    st.info("💡 Verifica que las credenciales en `.streamlit/secrets.toml` sean correctas y que tengas acceso a internet")
    st.stop()

# Crear tabs principales
tab1, tab2, tab3 = st.tabs([
    "🔢 Generación Individual",
    "📦 Impresión Masiva",
    "🔍 Búsqueda y Consulta"
])

# ============================================================================
# TAB 1: GENERACIÓN INDIVIDUAL
# ============================================================================
with tab1:
    st.header("Generación Individual de Código de Barras")
    st.markdown("Crea un nuevo código de barras ingresando el comodín del proveedor y el SKU TBC.")
    st.markdown("---")

    # Instrucciones de uso
    with st.expander("ℹ️ Instrucciones de Impresión"):
        st.markdown("""
        **Pasos para imprimir las etiquetas:**
        1. Completa el formulario y genera el código
        2. Descarga el archivo `.epl` generado
        3. Abre **Zebra Setup Utilities** en tu computadora
        4. Haz clic derecho en la impresora **GC420t**
        5. Selecciona **"Send File"**
        6. Elige el archivo `.epl` descargado
        7. Las etiquetas se imprimirán automáticamente

        **Importante:** Asegúrate de que la impresora esté encendida y las etiquetas cargadas.
        """)

    st.markdown("")

    # Formulario de generación
    with st.form("form_generacion_individual"):
        col1, col2, col3 = st.columns(3)

        with col1:
            comodin_input = st.text_input(
                "Comodín Proveedor *",
                max_chars=3,
                help="Identificador del proveedor (máximo 3 dígitos numéricos)",
                placeholder="Ej: 385"
            )

        with col2:
            sku_input = st.text_input(
                "TBC SKU *",
                max_chars=5,
                help="Código SKU del producto en TBC (máximo 5 dígitos numéricos)",
                placeholder="Ej: 98778"
            )

        with col3:
            cantidad_input = st.number_input(
                "Cantidad de copias *",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                help="Número de etiquetas a imprimir (1-100)"
            )
            if cantidad_input > 50:
                st.caption("⚠️ Cantidad grande, verifica material de impresora")

        st.markdown("")
        submitted = st.form_submit_button("🔢 Generar Código de Barras", use_container_width=True, type="primary")

    # Procesar formulario
    if submitted:
        # Validar inputs
        es_valido, mensaje_error = bg.validar_inputs(comodin_input, sku_input)

        if not es_valido:
            st.error(f"❌ Error de validación: {mensaje_error}")
        else:
            # Validar cantidad
            es_valido_cant, mensaje_error_cant = epl.validar_cantidad(cantidad_input)

            if not es_valido_cant:
                st.error(f"❌ Error en cantidad: {mensaje_error_cant}")
            else:
                with st.spinner("Generando código de barras..."):
                    try:
                        # Generar código
                        codigo_barras = bg.generar_codigo(comodin_input, sku_input)

                        # Verificar si ya existe
                        if db.verificar_codigo_existe(codigo_barras):
                            st.error(f"❌ El código de barras **{codigo_barras}** ya existe en la base de datos")
                            st.info("💡 **Solución:** Usa la pestaña '🔍 Búsqueda y Consulta' para reimprimir códigos existentes, o verifica el comodín y SKU ingresados")
                        else:
                            # Crear registro en Supabase
                            registro = db.crear_codigo_barras(comodin_input, sku_input)

                            if registro:
                                # Generar archivo EPL
                                contenido_epl = epl.generar_epl_individual(codigo_barras, cantidad_input)

                                # Mostrar éxito
                                st.success(f"✅ ¡Código de barras generado exitosamente!")

                                # Mostrar detalles
                                col_info1, col_info2, col_info3 = st.columns(3)
                                with col_info1:
                                    st.metric("Código de Barras", codigo_barras)
                                with col_info2:
                                    st.metric("Comodín", comodin_input.zfill(3))
                                with col_info3:
                                    st.metric("SKU", sku_input.zfill(5))

                                st.markdown("")

                                # Botón de descarga
                                st.download_button(
                                    label=f"📥 Descargar {codigo_barras}.epl ({cantidad_input} {'copia' if cantidad_input == 1 else 'copias'})",
                                    data=contenido_epl,
                                    file_name=f"{codigo_barras}.epl",
                                    mime="application/octet-stream",
                                    use_container_width=True,
                                    type="primary"
                                )

                                st.info("💡 Descarga el archivo y envíalo a la impresora usando Zebra Setup Utilities")

                            else:
                                st.error("❌ Error al crear el registro en la base de datos")
                                st.info("💡 **Posibles causas:**\n- Problemas de conexión a internet\n- El código puede estar duplicado por otro usuario\n- Verifica los permisos de la base de datos")

                    except ValueError as ve:
                        st.error(f"❌ Error de validación: {str(ve)}")
                    except Exception as e:
                        st.error(f"❌ Error inesperado: {str(e)}")

# ============================================================================
# TAB 2: IMPRESIÓN MASIVA
# ============================================================================
with tab2:
    st.header("Impresión Masiva de Códigos de Barras")
    st.markdown("Filtra y selecciona múltiples códigos para imprimir en lote.")
    st.markdown("---")

    # Inicializar session_state para resultados filtrados
    if "codigos_filtrados" not in st.session_state:
        st.session_state.codigos_filtrados = []

    # Sección de filtros
    st.subheader("🔍 Filtros")

    col_filtro1, col_filtro2, col_filtro3 = st.columns([2, 2, 3])

    with col_filtro1:
        # Obtener comodines únicos de la base de datos
        comodines_disponibles = db.obtener_comodines_unicos()

        if comodines_disponibles:
            opciones_comodin = ["Todos"] + comodines_disponibles
        else:
            opciones_comodin = ["Todos"]

        comodin_filtro = st.selectbox(
            "Comodín Proveedor",
            options=opciones_comodin,
            help="Filtra códigos por comodín específico"
        )

        if not comodines_disponibles:
            st.caption("⚠️ No hay códigos en la base de datos")

    with col_filtro2:
        estado_filtro = st.radio(
            "Estado de Impresión",
            options=["Todos", "No Impresos", "Impresos"],
            horizontal=False,
            help="Filtra por estado de impresión"
        )

    with col_filtro3:
        usar_fecha = st.checkbox("Usar filtro de fecha", value=False)

        if usar_fecha:
            fecha_desde = st.date_input(
                "Fecha desde",
                value=None,
                help="Fecha inicial de creación"
            )
            fecha_hasta = st.date_input(
                "Fecha hasta",
                value=None,
                help="Fecha final de creación"
            )
        else:
            fecha_desde = None
            fecha_hasta = None

    # Botón para aplicar filtros
    if st.button("🔎 Aplicar Filtros", use_container_width=True, type="primary"):
        # Validar fechas si están activas
        error_fechas = False
        if usar_fecha and fecha_desde and fecha_hasta:
            if fecha_hasta < fecha_desde:
                st.error("❌ La fecha hasta debe ser mayor o igual a la fecha desde")
                error_fechas = True

        if not error_fechas:
            with st.spinner("Buscando códigos..."):
                # Construir diccionario de filtros
                filtros = {}

                # Filtro de comodín
                if comodin_filtro != "Todos":
                    filtros["comodin"] = comodin_filtro

                # Filtro de estado
                if estado_filtro == "Impresos":
                    filtros["impreso"] = True
                elif estado_filtro == "No Impresos":
                    filtros["impreso"] = False
                # Si es "Todos", no agregamos filtro

                # Filtro de fechas
                if usar_fecha:
                    if fecha_desde:
                        filtros["fecha_desde"] = datetime.combine(fecha_desde, datetime.min.time())
                    if fecha_hasta:
                        filtros["fecha_hasta"] = datetime.combine(fecha_hasta, datetime.max.time())

                # Obtener códigos filtrados
                st.session_state.codigos_filtrados = db.obtener_codigos(filtros)

    st.markdown("---")

    # Mostrar resultados
    if st.session_state.codigos_filtrados:
        st.success(f"✅ Se encontraron **{len(st.session_state.codigos_filtrados)}** códigos")
        st.markdown("")

        # Inicializar session_state para selección de códigos
        if "seleccion_batch" not in st.session_state:
            st.session_state.seleccion_batch = {}

        st.subheader("📋 Selecciona los códigos a imprimir")
        st.markdown("Marca los códigos que deseas incluir en el lote y define la cantidad de copias.")

        # Límite de visualización para mejor rendimiento
        LIMITE_VISUALIZACION = 50
        total_codigos = len(st.session_state.codigos_filtrados)

        if total_codigos > LIMITE_VISUALIZACION:
            st.warning(f"⚠️ Se encontraron {total_codigos} códigos. Mostrando los primeros {LIMITE_VISUALIZACION} para mejor rendimiento. Usa filtros más específicos para reducir resultados.")

        st.markdown("")

        # Contenedor para la lista de códigos
        # Mostrar encabezado de la tabla
        col_header1, col_header2, col_header3, col_header4, col_header5 = st.columns([1, 2, 2, 2, 2])
        with col_header1:
            st.markdown("**Seleccionar**")
        with col_header2:
            st.markdown("**Código de Barras**")
        with col_header3:
            st.markdown("**TBC SKU**")
        with col_header4:
            st.markdown("**Comodín**")
        with col_header5:
            st.markdown("**Copias**")

        st.markdown("---")

        # Iterar sobre códigos filtrados (con límite)
        codigos_a_mostrar = st.session_state.codigos_filtrados[:LIMITE_VISUALIZACION]

        for idx, codigo in enumerate(codigos_a_mostrar):
            codigo_id = codigo['id']
            codigo_barras = codigo['codigo_barras']
            tbc_sku = codigo['tbc_sku']
            comodin = codigo['comodin_proveedor']

            # Crear columnas para cada fila
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 2])

            with col1:
                # Checkbox para seleccionar el código
                selected = st.checkbox(
                    "Seleccionar",
                    key=f"checkbox_{codigo_id}",
                    label_visibility="collapsed"
                )

            with col2:
                st.text(codigo_barras)

            with col3:
                st.text(tbc_sku)

            with col4:
                st.text(comodin)

            with col5:
                # Number input visible solo si el checkbox está activo
                if selected:
                    cantidad = st.number_input(
                        "Cantidad",
                        min_value=1,
                        max_value=100,
                        value=st.session_state.seleccion_batch.get(codigo_id, {}).get("cantidad", 1),
                        step=1,
                        key=f"cantidad_{codigo_id}",
                        label_visibility="collapsed"
                    )

                    # Guardar selección en session_state
                    st.session_state.seleccion_batch[codigo_id] = {
                        "codigo_barras": codigo_barras,
                        "cantidad": cantidad,
                        "comodin": comodin,
                        "tbc_sku": tbc_sku
                    }
                else:
                    # Si el checkbox no está activo, remover de selección
                    if codigo_id in st.session_state.seleccion_batch:
                        del st.session_state.seleccion_batch[codigo_id]
                    st.text("-")

            # Separador visual
            if idx < len(codigos_a_mostrar) - 1:
                st.markdown("")

        st.markdown("---")

        # Footer con preview del total
        codigos_seleccionados = len(st.session_state.seleccion_batch)
        etiquetas_totales = sum(item["cantidad"] for item in st.session_state.seleccion_batch.values())

        if codigos_seleccionados > 0:
            col_preview1, col_preview2 = st.columns(2)

            with col_preview1:
                st.metric(
                    label="Códigos Seleccionados",
                    value=codigos_seleccionados
                )

            with col_preview2:
                st.metric(
                    label="Total de Etiquetas",
                    value=etiquetas_totales
                )

            st.info(f"📦 **Resumen:** Se generarán {etiquetas_totales} etiquetas de {codigos_seleccionados} código{'s' if codigos_seleccionados != 1 else ''} diferente{'s' if codigos_seleccionados != 1 else ''}")

            st.markdown("")

            # Warning para grandes cantidades
            if etiquetas_totales > 50:
                st.warning(f"⚠️ Vas a imprimir {etiquetas_totales} etiquetas. Verifica que tengas suficiente material en la impresora.")

            # Checkbox de confirmación para operación masiva
            confirmar_batch = st.checkbox(
                f"Confirmo que deseo generar {etiquetas_totales} etiquetas y actualizar el estado de {codigos_seleccionados} código(s) en la base de datos",
                value=False,
                help="Esta acción actualizará el estado de impresión de los códigos seleccionados"
            )

            st.markdown("")

            # Botón para generar lote (disabled si no confirma)
            if st.button(
                "📥 Descargar lote completo",
                use_container_width=True,
                type="primary",
                disabled=not confirmar_batch
            ):
                with st.spinner("Generando lote EPL..."):
                    try:
                        # Recopilar códigos seleccionados con cantidades
                        codigos_y_cantidades = [
                            (item["codigo_barras"], item["cantidad"])
                            for item in st.session_state.seleccion_batch.values()
                        ]

                        # Generar EPL batch
                        contenido_epl_batch = epl.generar_epl_batch(codigos_y_cantidades)

                        # Actualizar estado impreso en DB
                        codigo_ids = list(st.session_state.seleccion_batch.keys())
                        actualizacion_exitosa = db.actualizar_estado_impreso(codigo_ids)

                        if actualizacion_exitosa:
                            # Generar timestamp para nombre de archivo
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            nombre_archivo = f"lote_{timestamp}.epl"

                            # Mostrar éxito
                            st.success("✅ ¡Lote generado exitosamente!")

                            # Botón de descarga
                            st.download_button(
                                label=f"📥 Descargar {nombre_archivo} ({etiquetas_totales} etiquetas)",
                                data=contenido_epl_batch,
                                file_name=nombre_archivo,
                                mime="application/octet-stream",
                                use_container_width=True,
                                type="primary"
                            )

                            st.info("💡 El estado de impresión de los códigos seleccionados ha sido actualizado en la base de datos")

                            # Opción de limpiar selección
                            if st.button("🔄 Limpiar selección y buscar nuevamente", use_container_width=True):
                                st.session_state.seleccion_batch = {}
                                st.rerun()

                        else:
                            st.error("❌ Error al actualizar el estado de impresión en la base de datos")
                            st.warning("⚠️ **Importante:** El archivo EPL se generó correctamente, pero el estado en la BD no se actualizó. Los códigos pueden marcarse como 'No Impresos' aunque ya se hayan generado.")

                    except Exception as e:
                        st.error(f"❌ Error al generar lote: {str(e)}")

        else:
            st.info("💡 Selecciona al menos un código para generar el lote")

    elif "codigos_filtrados" in st.session_state and len(st.session_state.codigos_filtrados) == 0:
        st.warning("⚠️ No se encontraron códigos con los filtros aplicados")
    else:
        st.info("💡 Aplica filtros para ver los códigos disponibles")

# ============================================================================
# TAB 3: BÚSQUEDA Y CONSULTA
# ============================================================================
with tab3:
    st.header("Búsqueda y Consulta de Códigos")
    st.markdown("Busca códigos existentes por código de barras o TBC SKU.")
    st.markdown("---")

    # Inicializar session_state para resultado de búsqueda
    if "resultado_busqueda" not in st.session_state:
        st.session_state.resultado_busqueda = None

    # Sección de búsqueda
    st.subheader("🔍 Buscar Código")

    col_busqueda1, col_busqueda2 = st.columns([3, 1])

    with col_busqueda1:
        query_busqueda = st.text_input(
            "Ingresa el Código de Barras (8 dígitos) o TBC SKU",
            placeholder="Ej: 38598778 o 98778",
            help="Busca por código de barras completo o por SKU TBC"
        )

    with col_busqueda2:
        st.markdown("")  # Espaciado para alinear el botón
        buscar_clicked = st.button("🔎 Buscar", use_container_width=True, type="primary")

    # Realizar búsqueda
    if buscar_clicked:
        if not query_busqueda or not query_busqueda.strip():
            st.error("❌ Por favor ingresa un código de barras o SKU para buscar")
        else:
            # Limpiar y validar query
            query_limpia = query_busqueda.strip()

            # Validar que solo contenga números
            if not query_limpia.isdigit():
                st.error("❌ El código de barras o SKU debe contener solo números")
            elif len(query_limpia) > 8:
                st.error("❌ El código no puede tener más de 8 dígitos")
            else:
                with st.spinner("Buscando código..."):
                    resultado = db.buscar_codigo(query_limpia)
                    st.session_state.resultado_busqueda = resultado

    st.markdown("---")

    # Mostrar resultados de búsqueda
    if st.session_state.resultado_busqueda:
        codigo = st.session_state.resultado_busqueda

        st.success("✅ Código encontrado")
        st.markdown("")

        # Card con detalles del código
        with st.container():
            st.subheader("📋 Detalles del Código")

            # Información principal en columnas
            col_det1, col_det2, col_det3, col_det4 = st.columns(4)

            with col_det1:
                st.metric(
                    label="Código de Barras",
                    value=codigo['codigo_barras']
                )

            with col_det2:
                st.metric(
                    label="Comodín",
                    value=codigo['comodin_proveedor']
                )

            with col_det3:
                st.metric(
                    label="TBC SKU",
                    value=codigo['tbc_sku']
                )

            with col_det4:
                estado_impreso = "✅ Impreso" if codigo['impreso'] else "⚠️ No Impreso"
                st.metric(
                    label="Estado",
                    value=estado_impreso
                )

            st.markdown("")

            # Información adicional
            col_info1, col_info2 = st.columns(2)

            with col_info1:
                fecha_creacion = datetime.fromisoformat(codigo['fecha_creacion'].replace('Z', '+00:00'))
                st.info(f"📅 **Fecha de Creación:** {fecha_creacion.strftime('%d/%m/%Y %H:%M:%S')}")

            with col_info2:
                if codigo['impreso'] and codigo['fecha_impresion']:
                    fecha_impresion = datetime.fromisoformat(codigo['fecha_impresion'].replace('Z', '+00:00'))
                    st.info(f"🖨️ **Última Impresión:** {fecha_impresion.strftime('%d/%m/%Y %H:%M:%S')}")
                else:
                    st.info("🖨️ **Última Impresión:** Nunca impreso")

        st.markdown("---")

        # Sección de reimpresión
        st.subheader("🖨️ Reimprimir Código")
        st.markdown("Genera un archivo EPL para reimprimir este código sin modificar su estado en la base de datos.")
        st.markdown("")

        col_reimp1, col_reimp2 = st.columns([1, 3])

        with col_reimp1:
            cantidad_reimp = st.number_input(
                "Cantidad de copias",
                min_value=1,
                max_value=100,
                value=1,
                step=1,
                help="Número de etiquetas a reimprimir"
            )

        with col_reimp2:
            st.markdown("")  # Espaciado
            if st.button("🖨️ Reimprimir Código", use_container_width=True, type="primary"):
                with st.spinner("Generando archivo EPL..."):
                    try:
                        # Generar EPL sin cambiar estado en DB
                        contenido_epl_reimp = epl.generar_epl_individual(
                            codigo['codigo_barras'],
                            cantidad_reimp
                        )

                        # Mostrar éxito
                        st.success("✅ ¡Archivo EPL generado exitosamente!")

                        # Botón de descarga
                        st.download_button(
                            label=f"📥 Descargar {codigo['codigo_barras']}.epl ({cantidad_reimp} {'copia' if cantidad_reimp == 1 else 'copias'})",
                            data=contenido_epl_reimp,
                            file_name=f"{codigo['codigo_barras']}.epl",
                            mime="application/octet-stream",
                            use_container_width=True,
                            type="primary"
                        )

                        st.info("💡 La reimpresión NO modifica el estado del código en la base de datos")

                    except Exception as e:
                        st.error(f"❌ Error al generar archivo: {str(e)}")

    elif st.session_state.resultado_busqueda is None and buscar_clicked:
        st.warning("⚠️ No se encontró ningún código con ese valor")
        st.info("💡 Verifica que el código de barras o SKU sea correcto")
    else:
        st.info("💡 Ingresa un código de barras o TBC SKU y presiona 'Buscar' para consultar")

# Footer
st.markdown("---")
st.caption("JYE Barcode System v1.0 | Didácticos Jugando y Educando")
