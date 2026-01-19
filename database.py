"""
Database module for JYE Barcode System
Handles all Supabase interactions
"""

import streamlit as st
from supabase import create_client, Client
from datetime import datetime
from typing import Optional, List, Dict, Any


def get_supabase_client() -> Client:
    """
    Inicializa y retorna el cliente de Supabase usando secrets de Streamlit

    Returns:
        Client: Cliente de Supabase configurado
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {str(e)}")
        raise


def crear_codigo_barras(comodin: str, sku: str) -> Optional[Dict[str, Any]]:
    """
    Crea un nuevo registro de código de barras en Supabase

    Args:
        comodin: Código comodín del proveedor (será padded a 3 dígitos)
        sku: SKU TBC (será padded a 5 dígitos)

    Returns:
        dict: Registro creado con todos los campos
        None: Si hay error
    """
    try:
        supabase = get_supabase_client()

        # Generar código de barras con padding
        codigo_barras = comodin.zfill(3) + sku.zfill(5)

        # Preparar datos para inserción
        datos = {
            "codigo_barras": codigo_barras,
            "comodin_proveedor": comodin,
            "tbc_sku": sku,
            "impreso": False
        }

        # Insertar en Supabase
        response = supabase.table("codigos_barras").insert(datos).execute()

        if response.data:
            return response.data[0]
        else:
            return None

    except Exception as e:
        st.error(f"Error al crear código de barras: {str(e)}")
        return None


def verificar_codigo_existe(codigo_barras: str) -> bool:
    """
    Verifica si un código de barras ya existe en la base de datos

    Args:
        codigo_barras: Código de barras de 8 dígitos a verificar

    Returns:
        bool: True si existe, False si no existe
    """
    try:
        supabase = get_supabase_client()

        response = supabase.table("codigos_barras")\
            .select("id")\
            .eq("codigo_barras", codigo_barras)\
            .execute()

        return len(response.data) > 0

    except Exception as e:
        st.error(f"Error al verificar código existente: {str(e)}")
        return False


def obtener_codigos(filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Obtiene códigos de barras con filtros opcionales

    Args:
        filtros: Diccionario con filtros opcionales:
            - comodin: str (filtra por comodín específico)
            - impreso: bool (filtra por estado de impresión)
            - fecha_desde: datetime (fecha inicial)
            - fecha_hasta: datetime (fecha final)

    Returns:
        list: Lista de registros que cumplen los filtros
    """
    try:
        supabase = get_supabase_client()

        # Iniciar query
        query = supabase.table("codigos_barras").select("*")

        # Aplicar filtros si existen
        if filtros:
            if "comodin" in filtros and filtros["comodin"]:
                query = query.eq("comodin_proveedor", filtros["comodin"])

            if "impreso" in filtros and filtros["impreso"] is not None:
                query = query.eq("impreso", filtros["impreso"])

            if "fecha_desde" in filtros and filtros["fecha_desde"]:
                query = query.gte("fecha_creacion", filtros["fecha_desde"].isoformat())

            if "fecha_hasta" in filtros and filtros["fecha_hasta"]:
                query = query.lte("fecha_creacion", filtros["fecha_hasta"].isoformat())

        # Ordenar por fecha de creación descendente
        query = query.order("fecha_creacion", desc=True)

        # Ejecutar query
        response = query.execute()

        return response.data if response.data else []

    except Exception as e:
        st.error(f"Error al obtener códigos: {str(e)}")
        return []


def actualizar_estado_impreso(codigo_ids: List[str]) -> bool:
    """
    Actualiza el estado de impresión de múltiples códigos

    Args:
        codigo_ids: Lista de UUIDs de códigos a actualizar

    Returns:
        bool: True si la actualización fue exitosa, False si hubo error
    """
    try:
        supabase = get_supabase_client()

        # Actualizar estado para cada código
        for codigo_id in codigo_ids:
            supabase.table("codigos_barras")\
                .update({
                    "impreso": True,
                    "fecha_impresion": datetime.now().isoformat()
                })\
                .eq("id", codigo_id)\
                .execute()

        return True

    except Exception as e:
        st.error(f"Error al actualizar estado de impresión: {str(e)}")
        return False


def buscar_codigo(query: str) -> Optional[Dict[str, Any]]:
    """
    Busca un código de barras por código completo o por TBC_SKU

    Args:
        query: Cadena de búsqueda (código de barras o SKU)

    Returns:
        dict: Registro encontrado
        None: Si no se encuentra
    """
    try:
        supabase = get_supabase_client()

        # Intentar buscar por código de barras primero
        response = supabase.table("codigos_barras")\
            .select("*")\
            .eq("codigo_barras", query)\
            .execute()

        if response.data and len(response.data) > 0:
            return response.data[0]

        # Si no se encuentra, buscar por TBC_SKU
        response = supabase.table("codigos_barras")\
            .select("*")\
            .eq("tbc_sku", query)\
            .execute()

        if response.data and len(response.data) > 0:
            return response.data[0]

        return None

    except Exception as e:
        st.error(f"Error al buscar código: {str(e)}")
        return None


def obtener_comodines_unicos() -> List[str]:
    """
    Obtiene lista de comodines únicos existentes en la base de datos

    Returns:
        list: Lista de comodines únicos ordenados
    """
    try:
        supabase = get_supabase_client()

        # Obtener todos los comodines
        response = supabase.table("codigos_barras")\
            .select("comodin_proveedor")\
            .execute()

        if response.data:
            # Extraer comodines únicos y ordenar
            comodines = list(set([item["comodin_proveedor"] for item in response.data]))
            comodines.sort()
            return comodines

        return []

    except Exception as e:
        st.error(f"Error al obtener comodines únicos: {str(e)}")
        return []
