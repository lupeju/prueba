
# TravelSmart MVP 🌍

TravelSmart is a multi-agent system built with **LangGraph** and **Azure OpenAI** to plan your perfect trip.

## Features
- **SurveyAgent**: Collects your core travel preferences.
- **FollowUpAgent**: Asks intelligent dynamic questions based on your profile.
- **DestinationAgent**: Proposes the best destination with justification.
- **ScraperAgent**: Fetches real-world points of interest from Wikipedia/Wikivoyage.
- **PlannerAgent**: Calculates a mathematical budget split and day-by-day itinerary.
- **PresenterAgent**: Formats everything into a beautiful Markdown report.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials.

3. **Run Application**:
   ```bash
   streamlit run app.py
   ```

## Architecture
- **Frontend**: Streamlit
- **Orchestration**: LangGraph (StateGraph)
- **Database**: SQLite (local `travelsmart.db`)
- **LLM**: Azure OpenAI
