
import streamlit as st
import uuid
from db import TravelDB
from graph import graph

# Page config
st.set_page_config(page_title="TravelSmart AI", page_icon="🌍", layout="wide")

# Persistent Storage
db = TravelDB()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "step" not in st.session_state:
    st.session_state.step = "survey"
if "travel_data" not in st.session_state:
    st.session_state.travel_data = {}

def save_state():
    db.save_session(st.session_state.session_id, st.session_state.travel_data)

st.title("🌍 TravelSmart: Tu Planificador Multi-Agente")
st.sidebar.info(f"Sesión: {st.session_state.session_id}")

# --- STEP 1: SURVEY ---
if st.session_state.step == "survey":
    st.header("📝 Cuéntanos sobre tu viaje ideal")
    
    with st.form("survey_form"):
        col1, col2 = st.columns(2)
        with col1:
            personas = st.selectbox("¿Con quién viajas?", ["Solo", "Pareja", "Grupo 3-5"])
            edades = st.selectbox("Rango de edad", ["18-25", "26-35", "36-50", "50+"])
            estilo = st.selectbox("Estilo preferido", ["Playa", "Montaña", "Ciudad", "Rural", "Mixto"])
            ritmo = st.select_slider("Ritmo del viaje", options=["Relax", "Equilibrado", "A tope"])
        
        with col2:
            intereses = st.multiselect("Intereses", ["Cultura", "Naturaleza", "Gastronomía", "Fiesta", "Museos", "Senderismo", "Compras"])
            presupuesto = st.selectbox("Presupuesto total (€)", ["300-600", "600-1000", "1000-1500", "1500-2500", "2500+"])
            duracion = st.selectbox("Duración", ["2-3 días", "4-5 días", "6-7 días", "8-10 días"])
            restricciones = st.multiselect("Restricciones", ["Sin avión", "Accesibilidad", "Vegetariano", "Niños", "Mascotas"])

        submitted = st.form_submit_button("Siguiente")
        if submitted:
            profile = {
                "personas": personas,
                "edades": edades,
                "estilo": estilo,
                "ritmo": ritmo,
                "intereses": intereses,
                "presupuesto_total": presupuesto,
                "duracion": duracion,
                "restricciones": restricciones
            }
            st.session_state.travel_data["perfil_base"] = profile
            
            # Run FollowUpAgent via Graph (Partial execution)
            with st.spinner("Generando preguntas personalizadas..."):
                initial_state = {"perfil_base": profile}
                # We only need the follow_up node output for now
                config = {"configurable": {"thread_id": st.session_state.session_id}}
                # Note: For simplicity in this MVP, we simulate the graph node call for dynamic UI
                from graph import follow_up_node
                res = follow_up_node(initial_state)
                st.session_state.travel_data["preguntas_extra"] = res["preguntas_extra"]
            
            st.session_state.step = "followup"
            save_state()
            st.rerun()

# --- STEP 2: FOLLOW UP ---
elif st.session_state.step == "followup":
    st.header("🔍 Unos detalles más...")
    preguntas = st.session_state.travel_data.get("preguntas_extra", [])
    
    with st.form("followup_form"):
        respuestas = {}
        for q in preguntas:
            respuestas[f"q_{q['id']}"] = st.radio(q["texto"], q["opciones"])
        
        submitted = st.form_submit_button("Ver Propuesta de Destino")
        if submitted:
            st.session_state.travel_data["respuestas_extra"] = respuestas
            
            # Run DestinationAgent
            with st.spinner("Analizando el mejor destino para ti..."):
                from graph import destination_node
                state = {
                    "perfil_base": st.session_state.travel_data["perfil_base"],
                    "respuestas_extra": respuestas
                }
                res = destination_node(state)
                st.session_state.travel_data.update(res)
            
            st.session_state.step = "destination"
            save_state()
            st.rerun()

# --- STEP 3: DESTINATION ---
elif st.session_state.step == "destination":
    st.header(f"📍 Destino Propuesto: {st.session_state.travel_data['destino']}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("¿Por qué este lugar?")
        for point in st.session_state.travel_data.get("justificacion", []):
            st.write(f"- {point}")
    
    with col2:
        st.subheader("Otras opciones")
        for alt in st.session_state.travel_data.get("alternativas", []):
            st.write(f"• {alt}")

    if st.button("Confirmar y Generar Plan Completo"):
        with st.spinner("Agentes trabajando: Scrapeando, Planificando y Diseñando..."):
            # Execute full graph from current state
            # In a real app we'd use graph.stream or invoke with correct starting point
            from graph import scraper_node, planner_node, presenter_node
            
            s_res = scraper_node(st.session_state.travel_data)
            st.session_state.travel_data.update(s_res)
            
            p_res = planner_node(st.session_state.travel_data)
            st.session_state.travel_data.update(p_res)
            
            pr_res = presenter_node(st.session_state.travel_data)
            st.session_state.travel_data.update(pr_res)
            
            st.session_state.step = "result"
            save_state()
            st.rerun()

# --- STEP 4: RESULT ---
elif st.session_state.step == "result":
    st.markdown(st.session_state.travel_data.get("output_final", "# Error al generar el plan"))
    
    if st.button("Empezar de nuevo"):
        st.session_state.step = "survey"
        st.session_state.travel_data = {}
        st.rerun()
