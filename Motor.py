import pandas as pd
import os
from datetime import datetime

# Encontrar automáticamente la carpeta real donde vive este archivo motor.py
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))

# Rutas exactas usando os.path.join para evitar problemas de compatibilidad
# NOTA: Cambia 'datos' por el nombre de tu carpeta si están dentro de un subdirectorio.
# Si están en la misma carpeta que motor.py, elimina el parámetro 'datos'.
ARCHIVO_ORIGINAL = os.path.join(CARPETA_ACTUAL, 'datos','control_solicitudes torno.csv')
ARCHIVO_LIMPIO = os.path.join(CARPETA_ACTUAL, 'datos','control_solicitudes_torno_limpio.csv')


def cargar_datos():
    """Carga los dos conjuntos de datos de manera segura."""
    try:
        # Leer el archivo original complementado
        df_original = pd.read_csv(ARCHIVO_ORIGINAL)
        print("✅ Archivo original cargado con éxito. Filas:", len(df_original))
        
        # Leer el archivo limpio optimizado para el dashboard
        df_limpio = pd.read_csv(ARCHIVO_LIMPIO)
        print("✅ Archivo limpio cargado con éxito. Filas:", len(df_limpio))
        
        return df_original, df_limpio
        
    except FileNotFoundError as e:
        print(f"❌ Error: No se encontró uno de los archivos. {e}")
        return None, None


def resumen_produccion():
    """Muestra estadísticas rápidas basadas en el archivo del Dashboard."""
    _, df_dash = cargar_datos()  # Usamos el guion bajo '_' para ignorar el original
    
    if df_dash is not None:
        print(f"\n--- RESUMEN GENERAL DEL TORNO (DASHBOARD) ---")
        print(f"Total de solicitudes registradas: {len(df_dash)}")
        print("\nDistribución por Estado:")
        print(df_dash['ESTADO'].value_counts().to_string())
        print("\nProducción Total por Operario:")
        print(df_dash.groupby('OPERARIO')['QTY'].sum().to_string())


def agregar_solicitud(solicitante, prioridad, nombre_pieza, material, cantidad, dimensiones="SEGUN MUESTRA", operario="Por Asignar"):
    """Crea una nueva orden de trabajo en ambos archivos para mantener la sincronización."""
    df_orig, df_dash = cargar_datos()
    
    if df_orig is not None and df_dash is not None:
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        
        # 1. Nueva fila básica para el registro original
        nueva_fila_orig = pd.DataFrame([{
            'SOLICITANTE': str(solicitante).title(),
            'PRIORIDAD': prioridad.upper(),
            'NOMBRE PIEZA': nombre_pieza.upper(),
            'MATERIAL': material.upper(),
            'DIMENSIONES': dimensiones,
            'QTY': int(cantidad),
            'FECHA SOLICITUD': fecha_hoy,
            'FECHA ENTREGA': None,
            'TIEMPO DEMORADO (DÍAS)': None,
            'ESTADO': 'EN PROCESO',
            'Observaciones': 'NUEVA ORDEN INGRESA A TALLER',
            'nro de remision': None
        }])
        
        # 2. Nueva fila con datos por defecto limpios para que el Dashboard no tenga Nulos
        nueva_fila_dash = pd.DataFrame([{
            'SOLICITANTE': str(solicitante).title(),
            'PRIORIDAD': prioridad.upper(),
            'NOMBRE PIEZA': nombre_pieza.upper(),
            'MATERIAL': material.upper(),
            'DIMENSIONES': dimensiones,
            'QTY': int(cantidad),
            'FECHA SOLICITUD': fecha_hoy,
            'FECHA ENTREGA': 'PENDIENTE',
            'TIEMPO DEMORADO (DÍAS)': '', # Vacío controlado para strings numéricos
            'ESTADO': 'EN PROCESO',
            'OPERARIO': operario.title(),
            'Observaciones': 'NUEVA ORDEN INGRESA A TALLER',
            'nro de remision': ''
        }])
        
        # Unir y salvar en archivo original
        df_orig = pd.concat([df_orig, nueva_fila_orig], ignore_index=True)
        df_orig.to_csv(ARCHIVO_ORIGINAL, index=False)
        
        # Unir y salvar en archivo limpio (Dashboard)
        df_dash = pd.concat([df_dash, nueva_fila_dash], ignore_index=True)
        df_dash.to_csv(ARCHIVO_LIMPIO, index=False)
        
        print(f"\n✅ ¡Orden de trabajo para la sede '{solicitante}' guardada exitosamente en ambos archivos!")


def marcar_entregado(indice_fila, operario_real=None):
    """Cambia el estado de una pieza a ENTREGADO en ambos archivos calculando el tiempo transcurrido."""
    df_orig, df_dash = cargar_datos()
    
    if df_orig is not None and df_dash is not None:
        if indice_fila >= len(df_dash):
            print("❌ Error: El índice de fila no existe.")
            return
            
        fecha_hoy_str = datetime.now().strftime("%d/%m/%Y")
        fecha_hoy_dt = datetime.now()
        
        # Obtener fecha de solicitud original para calcular los días reales demorados
        fecha_sol_str = df_dash.at[indice_fila, 'FECHA SOLICITUD']
        try:
            fecha_sol_dt = datetime.strptime(fecha_sol_str, "%d/%m/%Y")
            dias_demora = max(0, (fecha_hoy_dt - fecha_sol_dt).days)
        except Exception:
            dias_demora = 0 # En caso de que falle el parseo de la fecha
            
        # Conseguir el último número de remisión para seguir el consecutivo secuencial
        todos_los_nros = pd.to_numeric(df_dash['nro de remision'], errors='coerce')
        siguiente_remision = int(todos_los_nros.max() + 1) if not todos_los_nros.isna().all() else 4140

        # --- ACTUALIZAR ARCHIVO ORIGINAL ---
        df_orig.at[indice_fila, 'ESTADO'] = 'ENTREGADO'
        df_orig.at[indice_fila, 'FECHA ENTREGA'] = fecha_hoy_str
        df_orig.at[indice_fila, 'TIEMPO DEMORADO (DÍAS)'] = dias_demora
        df_orig.at[indice_fila, 'nro de remision'] = siguiente_remision
        df_orig.to_csv(ARCHIVO_ORIGINAL, index=False)
        
        # --- ACTUALIZAR ARCHIVO DEL DASHBOARD (LIMPIO) ---
        df_dash.at[indice_fila, 'ESTADO'] = 'ENTREGADO'
        df_dash.at[indice_fila, 'FECHA ENTREGA'] = fecha_hoy_str
        df_dash.at[indice_fila, 'TIEMPO DEMORADO (DÍAS)'] = int(dias_demora)
        df_dash.at[indice_fila, 'nro de remision'] = int(siguiente_remision)
        if operario_real:
            df_dash.at[indice_fila, 'OPERARIO'] = str(operario_real).title()
            
        df_dash.to_csv(ARCHIVO_LIMPIO, index=False)
        
        print(f"\n✅ ¡Fila {indice_fila} marcada como ENTREGADO! Remisión No. {siguiente_remision}. Demoró: {dias_demora} día(s).")


# ==========================================
# 🚀 EJEMPLO DE USO OPERACIONAL
# ==========================================
if __name__ == "__main__":
    print("--- INICIANDO MOTOR DEL SISTEMA ---")
    
    # 1. Ejecutar una revisión general de métricas en la terminal
    resumen_produccion()
    
    # 2. Descomenta estas líneas cuando quieras probar el ingreso de una nueva orden:
    # agregar_solicitud(
    #     solicitante="Bodytech Kennedy", 
    #     prioridad="MEDIA (FL)", 
    #     nombre_pieza="PIN PUSH LEG EXTENSION FZ", 
    #     material="ACERO PLATA", 
    #     cantidad=5, 
    #     dimensiones="1/2 x 4 pulg", 
    #     operario="Operario Dos"
    # )
    
    # 3. Descomenta esta línea para cerrar una orden existente (Ejemplo fila índice 4):
    # marcar_entregado(indice_fila=4, operario_real="Operario Tres")