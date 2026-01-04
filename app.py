import streamlit as st
import google.generativeai as genai
import pandas as pd

# 1. CONFIGURACIÓN DE PÁGINA E INTERFAZ
st.set_page_config(page_title="App PNI - Nacho Rey", layout="wide")
st.title("🧬 Asistente de Nutrición Integrativa PNI")
st.markdown("---")

# Configurar API Key desde Secrets de Streamlit
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 2. BASE DE DATOS MAESTRA (Simplificada para el código)
# En una versión avanzada, podrías cargar un CSV aquí
alimentos_pni = [
    {"Alimento": "Salmón Salvaje", "Cal": 208, "P": 20, "H": 0, "G": 13, "Micros": "D, B12, Se, Mg"},
    {"Alimento": "Lomo de Cerdo", "Cal": 143, "P": 26, "H": 0, "G": 3.5, "Micros": "B1, B6, Zn"},
    {"Alimento": "Huevo Gallina", "Cal": 155, "P": 13, "H": 1.1, "G": 11, "Micros": "A, D, B12, Colina"},
    {"Alimento": "Boniato", "Cal": 86, "P": 1.6, "H": 20, "G": 0.1, "Micros": "A, C, B6, K"},
    {"Alimento": "Arándanos", "Cal": 57, "P": 0.7, "H": 14, "G": 0.3, "Micros": "C, K, Antocianinas"},
    {"Alimento": "Espinacas", "Cal": 23, "P": 2.9, "H": 3.6, "G": 0.4, "Micros": "K, A, B9, Mg"},
    {"Alimento": "Nueces", "Cal": 654, "P": 15, "H": 13.7, "G": 65, "Micros": "B6, Mg, Polifenoles"},
    # ... la IA usará su conocimiento para el resto basándose en tu tabla maestra
]

# 3. BARRA LATERAL - ENTRADA DE DATOS DEL PACIENTE
with st.sidebar:
    st.header("Datos del Paciente")
    edad = st.number_input("Edad", min_value=1, max_value=120, value=44)
    estatura = st.number_input("Estatura (cm)", min_value=100, max_value=250, value=170)
    peso_actual = st.number_input("Peso Actual (kg)", min_value=30, max_value=250, value=70)
    peso_ideal = st.number_input("Peso Ideal (kg)", min_value=30, max_value=250, value=70)
    actividad = st.selectbox("Actividad Física", ["Sedentario (1.2)", "Ligero (1.375)", "Moderado (1.55)", "Intenso (1.725)"])
    fa = float(actividad.split("(")[1].replace(")", ""))

# 4. LÓGICA DE CÁLCULO NACHO REY
gmb = 66.5 + (13.75 * peso_ideal) + (5.003 * estatura) - (6.755 * edad)
get = gmb * fa
cal_objetivo = get - 500

# Macros Totales
prot_total = 1.9 * peso_ideal
gras_total = (cal_objetivo * 0.35) / 9
carb_total = (cal_objetivo - (prot_total * 4) - (gras_total * 9)) / 4

# 5. MOSTRAR RESULTADOS TÉCNICOS
col1, col2, col3, col4 = st.columns(4)
col1.metric("GMB", f"{int(gmb)} kcal")
col2.metric("GET", f"{int(get)} kcal")
col3.metric("Objetivo", f"{int(cal_objetivo)} kcal")
col4.metric("Déficit", "-500 kcal")

st.subheader("Distribución Diaria de Macronutrientes")
c1, c2, c3 = st.columns(3)
c1.warning(f"Proteína: {int(prot_total)}g")
c2.info(f"Carbohidratos: {int(carb_total)}g")
c3.success(f"Grasas: {int(gras_total)}g")

# 6. REPARTO POR COMIDAS
st.markdown("---")
st.subheader("Reparto por Tomas (Timing Nutricional)")
distribucion = {
    "Desayuno (20%)": [0.20],
    "Almuerzo (10%)": [0.10],
    "Comida (35%)": [0.35],
    "Merienda (10%)": [0.10],
    "Cena (25%)": [0.25]
}

data_reparto = []
for comida, porcentaje in distribucion.items():
    p = prot_total * porcentaje[0]
    h = carb_total * porcentaje[0]
    g = gras_total * porcentaje[0]
    cal = cal_objetivo * porcentaje[0]
    data_reparto.append({"Comida": comida, "Cal": int(cal), "P (g)": int(p), "H (g)": int(h), "G (g)": int(g)})

st.table(pd.DataFrame(data_reparto))

# 7. CHAT CON GEMINI PARA PROTOCOLO PERSONALIZADO
st.markdown("---")
st.subheader("Asistente PNI - Sugerencia de Menú y Patologías")
pregunta = st.text_input("Haz una pregunta sobre el protocolo (ej: ¿Qué alimentos con Magnesio añadir a la cena?)")

if pregunta:
    model = genai.GenerativeModel('gemini-pro')
    # Prompt con contexto de Nacho Rey
    prompt_context = f"""
    Eres Nacho Rey, Dietista Integrativo PNI.
    Datos paciente: {edad} años, {peso_actual}kg, peso ideal {peso_ideal}kg.
    Macros objetivo: P:{int(prot_total)}g, H:{int(carb_total)}g, G:{int(gras_total)}g.
    Usa tu tabla maestra de alimentos (Salmón, Cerdo, Búfala, Frutas, Verduras, etc).
    Pregunta del usuario: {pregunta}
    Responde de forma técnica pero empática, destacando vitaminas, minerales y bioactivos.
    """
    response = model.generate_content(prompt_context)
    st.write(response.text)

st.markdown("---")
st.caption("Firma: Nacho Rey - Dietista Integrativo | Nº Colegiado: 2122")
