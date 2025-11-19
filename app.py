import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
import os

# CONFIGURACIÓN DE LA PÁGINA INICIAL
st.set_page_config(page_title="Tecmi Gastitos / Gestor de gastos estudiantiles", page_icon="💸", layout="wide")
st.title("💸 Gestor de Gastos Estudiantiles / Tecmi Gastitos")
st.divider()

# --- FUNCION GUARDA LOS DATOS INGRESADOS EN EL APARTADO DE REGISTROS.CSV ---
def cargar_datos(filename="registros.csv"):
    """Carga los datos desde un archivo CSV. Si no existe, crea un DataFrame vacío."""
    if os.path.exists(filename):
        try:
            df = pd.read_csv(filename, parse_dates=['Fecha'])
            return df
        except Exception as e:
            st.error(f"Error al cargar los datos: {e}")
            return pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción"])
    return pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción"])

def guardar_datos(df, filename="registros.csv"):
    """Guarda el DataFrame en un archivo CSV."""
    try:
        df.to_csv(filename, index=False)
    except Exception as e:
        st.error(f"Error al guardar los datos: {e}")

# --- INICIALIZAR DATAFRAME EN SESSION STATE ---
# Carga los datos desde el archivo al iniciar la sesión.
if "gastos" not in st.session_state:
    st.session_state["gastos"] = cargar_datos()

# --- BARRA MENU ---
with st.sidebar:
    image_path = "tecmilogo.png"  # Asegúrate de tener el logo en el mismo directorio o ajusta la ruta
    st.image(image_path, use_container_width=True)
    st.divider()
    st.header("Menú")
    page = st.radio(
        "Ir a:",
        ["**Registro**", "**Historial**", "**Análisis** ", "**Ajustes**",], # Opciones actualizadas para la navegación
        index=0
    )
    st.divider()
    st.caption("COMO FUNCIONA `TECMIGASTITOS`")
    st.caption("**Registro:** Registrar tus gastos")
    st.caption("**Historial:** Historial de tus gastos registrados")
    st.caption("**Análisis:** Análisis y reportes de gastos totales registrados")
    st.divider()
    st.caption("💵 TECMI GASTITOS / 2025 💵")
# --- PÁGINA DE REGISTRO ---
if page == "**Registro**":
    st.header("➕ Registrar nuevo gasto")

    with st.form("form_gasto"):
        fecha = st.date_input("🗓️Fecha", value=date.today())
        categoria = st.selectbox("🔖Categoría", [
            "Alimentación", "Transporte", "Renta", "Colegiatura",
            "Libros y Material", "Salud", "Entretenimiento", "Servicios", "Otros"
        ])
        monto = st.number_input("💲Monto (MXN)", min_value=0.0, step=1.0)
        descripcion = st.text_input("📝Descripción (opcional)")
        
        submit = st.form_submit_button("Agregar gasto")

    if submit:
        # Validar que el monto sea mayor a cero
        if monto > 0:
            nuevo = pd.DataFrame(
                [[fecha, categoria, monto, descripcion]],
                columns=["Fecha", "Categoría", "Monto", "Descripción"]
            )
            # Asegurar que la columna Fecha sea de tipo datetime para ordenarla después
            nuevo['Fecha'] = pd.to_datetime(nuevo['Fecha'])
            
            st.session_state["gastos"] = pd.concat([st.session_state["gastos"], nuevo], ignore_index=True)
            guardar_datos(st.session_state["gastos"]) # Guardar los datos en el archivo
            st.success("✅ Gasto agregado correctamente")
        else:
            st.warning("⚠️ El monto debe ser mayor a $0.00")

# --- PÁGINA DE HISTORIAL ---
elif page == "**Historial**":
    st.header("📊 Historial de gastos")
    
    if not st.session_state["gastos"].empty:
        # Asegurarse que la columna Fecha es datetime para poder ordenarla
        st.session_state["gastos"]['Fecha'] = pd.to_datetime(st.session_state["gastos"]['Fecha'])
        
        # Ordenar los gastos del más reciente al más antiguo
        gastos_mostrados = st.session_state["gastos"].sort_values(by="Fecha", ascending=False).reset_index(drop=True)
        
        # Crear una copia para evitar advertencias de Streamlit al modificarla
        df_display = gastos_mostrados.copy()
        # Formatear la fecha para mostrarla sin la hora
        df_display['Fecha'] = df_display['Fecha'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(df_display, use_container_width=True)
        
        st.divider()
        
        # --- SECCIÓN PARA ELIMINAR GASTOS ---
        st.subheader("🗑️ Eliminar un gasto")
        if not gastos_mostrados.empty:
            indices_para_eliminar = st.multiselect(
                "Selecciona el(los) índice(s) del gasto a eliminar:",
                options=gastos_mostrados.index.tolist(),
                format_func=lambda x: f"Índice {x} - {gastos_mostrados.loc[x, 'Fecha'].strftime('%Y-%m-%d')} - ${gastos_mostrados.loc[x, 'Monto']:.2f} - {gastos_mostrados.loc[x, 'Categoría']}"
            )
            
            if st.button("Eliminar gastos seleccionados"):
                if indices_para_eliminar:
                    st.session_state["gastos"] = st.session_state["gastos"].drop(indices_para_eliminar).reset_index(drop=True)
                    guardar_datos(st.session_state["gastos"]) # Guardar los datos después de eliminar
                    st.success("Gasto(s) eliminado(s) correctamente.")
                    st.rerun() # Recargar la página para ver el cambio
                else:
                    st.warning("No has seleccionado ningún gasto para eliminar.")
    else:
        st.info("Aún no has registrado ningún gasto. Ve a la sección 'Registro' para empezar.")

# --- PÁGINA DE ANÁLISIS ---
elif page == "**Análisis**":
    st.header("📈 Análisis de Gastos")

    if not st.session_state["gastos"].empty:
        # Asegurarse que la columna Fecha es datetime
        df_analisis = st.session_state["gastos"].copy()
        df_analisis['Fecha'] = pd.to_datetime(df_analisis['Fecha'])
        
        # --- TABLA BONITA: RESUMEN POR CATEGORÍA ---
        st.subheader("📋 Resumen de gastos por categoría")
        resumen = df_analisis.groupby("Categoría", as_index=False)["Monto"].sum().sort_values(by="Monto", ascending=False)

        # Estilo bonito con pandas Styler
        styled_resumen = resumen.style.background_gradient(cmap="Blues").format({"Monto": "${:,.2f}"})
        st.write(styled_resumen)
        st.divider()

        # --- GRÁFICOS ---
        col1, col2 = st.columns(2)
        
        with col1:
            # --- GRÁFICO DE BARRAS DE GASTOS POR CATEGORÍA ---
            st.subheader("📊 Gráfico de barras")
            chart = alt.Chart(resumen).mark_bar().encode(
                x=alt.X('Monto', type='quantitative', title='Monto Total (MXN)'),
                y=alt.Y('Categoría', type='nominal', title='Categoría', sort='-x'),
                color=alt.Color('Categoría', legend=None),
                tooltip=['Categoría', 'Monto']
            ).properties(
                title='Gastos Totales por Categoría'
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            # --- GRÁFICO DE PASTEL (DONUT) ---
            st.subheader("🍩 Gráfico de pastel")
            pie_chart = alt.Chart(resumen).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Monto", type="quantitative"),
                color=alt.Color(field="Categoría", type="nominal", title="Categoría"),
                tooltip=['Categoría', 'Monto']
            ).properties(
                title='Distribución de Gastos'
            )
            st.altair_chart(pie_chart, use_container_width=True)
            
        st.divider()
        
        # --- ANÁLISIS POR FECHA ---
        st.subheader("📅 Gastos a lo largo del tiempo")
        line_chart = alt.Chart(df_analisis).mark_line(point=True).encode(
            x=alt.X('Fecha', type='temporal', title='Fecha'),
            y=alt.Y('Monto', type='quantitative', title='Monto (MXN)'),
            tooltip=['Fecha', 'Monto', 'Categoría', 'Descripción']
        ).properties(
            title='Gastos Registrados por Día'
        ).interactive()
        
        st.altair_chart(line_chart, use_container_width=True)

    else:
        st.info("No hay datos para analizar. Registra algunos gastos primero.")

# --- PÁGINA DE AJUSTES ---
elif page == "**Ajustes**":
    st.header("⚙️ Ajustes")
    st.subheader("🔄 Reiniciar datos")
    st.write("Esta acción eliminará todos los gastos registrados. Asegúrate de hacer una copia de seguridad si es necesario para evitar pérdidas.")
    
    if st.button("Reiniciar datos"):
        st.session_state["gastos"] = pd.DataFrame(columns=["Fecha", "Categoría", "Monto", "Descripción"])
        guardar_datos(st.session_state["gastos"]) # Guardar el DataFrame vacío
        st.success("✅ Datos reiniciados correctamente.")
        st.rerun()  # Recargar la página para reflejar los cambios