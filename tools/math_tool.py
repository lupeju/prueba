
from typing import Dict

def calculate_budget_allocation(total_budget: float, style: str) -> Dict[str, float]:
    """
    Calculates the budget split based on the travel style.
    Returns a dictionary with percentages and absolute values.
    """
    # Default allocation
    allocation = {
        "Alojamiento": 0.30,
        "Comida": 0.25,
        "Transporte Local": 0.15,
        "Actividades/Entradas": 0.20,
        "Imprevistos": 0.10
    }

    style_lower = style.lower()
    if "relax" in style_lower:
        allocation["Alojamiento"] = 0.45
        allocation["Actividades/Entradas"] = 0.10
    elif "a tope" in style_lower or "aventura" in style_lower:
        allocation["Actividades/Entradas"] = 0.40
        allocation["Alojamiento"] = 0.20
    elif "gastronomía" in style_lower:
        allocation["Comida"] = 0.40
        allocation["Alojamiento"] = 0.20

    # Ensure it sums to 1.0 (normalization just in case)
    total_alloc = sum(allocation.values())
    results = {k: round((v / total_alloc) * total_budget, 2) for k, v in allocation.items()}
    
    return results
