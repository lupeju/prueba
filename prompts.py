
FOLLOW_UP_PROMPT = """
Eres un agente experto en viajes. Basado en el siguiente perfil básico, genera de 3 a 5 preguntas de seguimiento de opción múltiple para refinar el viaje.
Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
{
  "preguntas": [
    {"id": 1, "texto": "¿...?", "opciones": ["A", "B", "C"]},
    ...
  ]
}

Perfil: {perfil}
"""

DESTINATION_PROMPT = """
Basado en el perfil enriquecido del usuario, propón 1 destino principal y 2 alternativas.
Perfil: {perfil}

Responde en JSON:
{
  "destino_principal": "Ciudad, País",
  "justificacion": ["punto 1", "punto 2"],
  "alternativas": ["Destino A", "Destino B"]
}
"""

PLANNER_PROMPT = """
Crea un itinerario detallado para {duracion} en {destino}.
Perfil del usuario: {perfil}
Actividades sugeridas (Scrapeadas): {actividades}

El itinerario debe ser organizado por días.
"""

PRESENTER_PROMPT = """
Eres el PresenterAgent. Formatea los siguientes datos en un Markdown atractivo para el usuario.
Incluye:
1. Resumen del Viajero.
2. Destino Recomendado + Justificación.
3. Itinerario por días.
4. Tabla de Presupuesto.
5. Tips (alojamiento, mejor época).
6. Fuentes de información.

Datos: {datos}
"""
