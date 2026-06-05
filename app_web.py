import streamlit as st
import Motor

st.divider()
st.subheader("📊 Control de Producción")

df_actual = Motor.cargar_datos()

if df_actual is not None:
    # 1. Aseguramos que la columna ESTADO existe
    if 'ESTADO' not in df_actual.columns:
        df_actual['ESTADO'] = 'PENDIENTE'
    
    # 2. Filtramos por "PENDIENTE" (ya que creamos esa categoría arriba)
    df_pendientes = df_actual[df_actual['ESTADO'] == 'PENDIENTE']
    
    if not df_pendientes.empty:
        st.write("### Trabajos activos:")
        st.dataframe(
            df_pendientes[['SOLICITANTE', 'PRIORIDAD', 'NOMBRE PIEZA', 'QTY', 'MATERIAL']], 
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.subheader("✅ Marcar trabajo como Entregado")
        
        # 3. Menú desplegable para seleccionar
        opciones = []
        for indice, fila in df_pendientes.iterrows():
            texto_opcion = f"Fila {indice} - {fila['QTY']}x {fila['NOMBRE PIEZA']} ({fila['SOLICITANTE']})"
            opciones.append(texto_opcion)
            
        trabajo_seleccionado = st.selectbox("Selecciona el trabajo terminado:", opciones)
        
        if st.button("Confirmar Entrega"):
            indice_real = int(trabajo_seleccionado.split(" ")[1])
            # Aquí llamamos a tu función de marcar entregado
            Motor.marcar_entregado(indice_real)
            st.success("¡Pieza entregada!")
            st.rerun()
            
    else:
        st.success("¡Excelente! No hay trabajos pendientes. Todo entregado.")
        # Opcional: mostrar la tabla completa de entregados si quieres ver el histórico
        with st.expander("Ver histórico de piezas entregadas"):
            st.dataframe(df_actual[df_actual['ESTADO'] == 'ENTREGADO'])
else:
    st.warning("No se encontró la base de datos.")
