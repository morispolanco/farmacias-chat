import streamlit as st
import subprocess
import json

# Título de la aplicación
st.title("PharmaChat Pro - Asistente para Farmacias")

# Descripción breve
st.write("Consulta medicamentos, obtén recomendaciones o capacita a tu equipo sin complicaciones.")

# Obtener la API Key desde los secrets de Streamlit
API_KEY = st.secrets["GEMINI_API_KEY"]

# Opciones de modo
modo = st.selectbox("Selecciona el modo:", 
                    ["Consulta de clientes", "Recomendación de productos", "Capacitación de empleados"])

# Entrada del usuario
entrada_usuario = st.text_area("Ingresa tu consulta o situación:", height=150)

# Función para generar contenido con Gémini usando curl
def generar_respuesta(entrada):
    # Definir el cuerpo JSON de la solicitud
    cuerpo_json = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": entrada}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,
            "responseMimeType": "text/plain"
        }
    }

    # Convertir el cuerpo JSON a una cadena
    cuerpo_str = json.dumps(cuerpo_json)

    # Construir el comando curl como una lista para evitar problemas de shell
    curl_cmd = [
        "curl",
        "-X", "POST",
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", cuerpo_str
    ]

    # Ejecutar el comando curl y capturar la salida
    try:
        resultado = subprocess.run(curl_cmd, capture_output=True, text=True, check=True)
        # Parsear la respuesta JSON
        respuesta_json = json.loads(resultado.stdout)
        return respuesta_json["candidates"][0]["content"]["parts"][0]["text"]
    except subprocess.CalledProcessError as e:
        return f"Error al procesar la solicitud: {e.stderr}"
    except (json.JSONDecodeError, KeyError):
        return "No se pudo obtener una respuesta válida. Intenta de nuevo."

# Botón para procesar la consulta
if st.button("Obtener respuesta"):
    if entrada_usuario:
        # Ajustar el prompt según el modo seleccionado
        if modo == "Consulta de clientes":
            prompt = f"Actúa como un asistente farmacéutico y responde esta consulta de un cliente: {entrada_usuario}. Proporciona información útil y segura, y advierte consultar a un médico si es necesario."
        elif modo == "Recomendación de productos":
            prompt = f"Actúa como un asistente farmacéutico y recomienda productos de venta libre basados en esta situación: {entrada_usuario}. Incluye sugerencias de upselling si aplica."
        else:  # Capacitación de empleados
            prompt = f"Actúa como un tutor farmacéutico y simula una interacción con un cliente basada en esta situación: {entrada_usuario}. Proporciona una respuesta modelo y retroalimentación para el empleado."

        # Generar la respuesta
        respuesta = generar_respuesta(prompt)
        st.subheader("Respuesta:")
        st.write(respuesta)
    else:
        st.warning("Por favor, ingresa una consulta o situación.")

# Nota al pie
st.markdown("---")
st.write("PharmaChat Pro - Potenciado por xAI y Gémini (simulación).")
