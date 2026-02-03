
import os
import json
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatAzureOpenAI
from dotenv import load_dotenv

from tools.math_tool import calculate_budget_allocation
from tools.scrape_tool import scrape_wikipedia_poi
import prompts

load_dotenv()

# State definition
class TravelState(TypedDict):
    perfil_base: Dict[str, Any]
    preguntas_extra: List[Dict[str, Any]]
    respuestas_extra: Dict[str, str]
    perfil_enriquecido: Dict[str, Any]
    destino: str
    justificacion: List[str]
    alternativas: List[str]
    actividades: List[Dict[str, str]]
    itinerary: str
    budget: Dict[str, float]
    output_final: str

# LLM setup
llm = ChatAzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.7
)

# Nodes
def follow_up_node(state: TravelState):
    print("[Agent] FollowUpAgent generating questions...")
    prompt = prompts.FOLLOW_UP_PROMPT.format(perfil=state["perfil_base"])
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        return {"preguntas_extra": data["preguntas"]}
    except:
        return {"preguntas_extra": [{"id": 1, "texto": "¿Prefiere hoteles céntricos o rurales?", "opciones": ["Céntrico", "Rural"]}]}

def destination_node(state: TravelState):
    print("[Agent] DestinationAgent picking a place...")
    profile = {**state["perfil_base"], **state.get("respuestas_extra", {})}
    prompt = prompts.DESTINATION_PROMPT.format(perfil=profile)
    res = llm.invoke(prompt)
    try:
        data = json.loads(res.content)
        return {
            "perfil_enriquecido": profile,
            "destino": data["destino_principal"],
            "justificacion": data["justificacion"],
            "alternativas": data["alternativas"]
        }
    except:
        return {
            "destino": "Tokio, Japón",
            "justificacion": ["Cultura vibrante", "Excelente comida"],
            "alternativas": ["Seúl", "Kyoto"]
        }

def scraper_node(state: TravelState):
    print(f"[Agent] ScraperAgent searching for activities in {state['destino']}...")
    city = state["destino"].split(",")[0]
    acts = scrape_wikipedia_poi(city)
    
    if not acts:
        print("[Warning] Scraping failed, using LLM fallback.")
        prompt = f"Genera una lista de 5 actividades turísticas famosas en {state['destino']}. Responde solo JSON list of strings."
        res = llm.invoke(prompt)
        try:
            fallback = json.loads(res.content)
            acts = [{"nombre": a, "fuente": "LLM Fallback", "url": "#"} for a in fallback]
        except:
            acts = [{"nombre": "Centro histórico", "fuente": "Generic", "url": "#"}]
            
    return {"actividades": acts}

def planner_node(state: TravelState):
    print("[Agent] PlannerAgent building itinerary and budget...")
    # Math Tool
    budget_total_str = state["perfil_base"]["presupuesto_total"]
    # Extract number from range "300-600" -> 450 approx
    try:
        parts = budget_total_str.split("-")
        val = (float(parts[0].replace("+","")) + float(parts[1])) / 2 if len(parts) > 1 else float(parts[0].replace("+",""))
    except:
        val = 1000.0
        
    budget_split = calculate_budget_allocation(val, state["perfil_base"]["estilo"])
    
    # Itinerary
    prompt = prompts.PLANNER_PROMPT.format(
        duracion=state["perfil_base"]["duracion"],
        destino=state["destino"],
        perfil=state["perfil_enriquecido"],
        actividades=state["actividades"]
    )
    res = llm.invoke(prompt)
    
    return {"budget": budget_split, "itinerary": res.content}

def presenter_node(state: TravelState):
    print("[Agent] PresenterAgent formatting output...")
    data_bundle = {
        "perfil": state["perfil_base"],
        "destino": state["destino"],
        "justificacion": state["justificacion"],
        "itinerary": state["itinerary"],
        "budget": state["budget"],
        "actividades": state["actividades"]
    }
    prompt = prompts.PRESENTER_PROMPT.format(datos=data_bundle)
    res = llm.invoke(prompt)
    return {"output_final": res.content}

# Workflow construction
def create_graph():
    workflow = StateGraph(TravelState)

    workflow.add_node("follow_up", follow_up_node)
    workflow.add_node("destination", destination_node)
    workflow.add_node("scraper", scraper_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("presenter", presenter_node)

    # Note: Survey is handled by Streamlit and starts the graph from follow_up
    workflow.set_entry_point("follow_up")
    workflow.add_edge("follow_up", "destination")
    workflow.add_edge("destination", "scraper")
    workflow.add_edge("scraper", "planner")
    workflow.add_edge("planner", "presenter")
    workflow.add_edge("presenter", END)

    return workflow.compile()

graph = create_graph()
