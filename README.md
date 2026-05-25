# Competitor Market Insights Service

A REST API built with **FastAPI** and **Google Agent Development Kit (ADK)** to gather and synthesize market insights on competitor products. The service uses **MongoDB** and **Beanie ODM** for data persistence.

The system spawns three specialized agents running **in parallel** via Google ADK:
1.  **Price Analyst**: Evaluates pricing tiers, models, and value-for-money metrics.
2.  **Sentiment Analyst**: Evaluates public customer sentiment, satisfaction, and pain points.
3.  **Marketing Analyst**: Evaluates marketing strategies, value propositions, target audience, and messaging.

All sub-agents are equipped with Google's native `google_search` tool for real-time grounding, and execute concurrently to minimize total request latency.

---

## Architecture Overview

The project is structured following a layered architecture design:

*   **Controller Layer (`app/api/v1/endpoints/insights.py`)**: Exposes REST API endpoints, handles requests, and returns Pydantic DTO responses.
*   **Service Layer (`app/services/insights_service.py`)**: Contains business logic, decides whether the input is a website or a name, writes the initial record to MongoDB, and dispatches background tasks.
*   **Agent Layer (`app/agents/market_agents.py`)**: Defines Google ADK agents, registers their tools, and orchestrates the parallel workflow.
*   **Repository Layer (`app/repositories/models.py`)**: Handles MongoDB document modeling using Beanie ODM.
*   **DTOs (`app/dtos/insights_dtos.py`)**: Standardizes JSON request/response formats.

---

## Requirements

*   Python >= 3.10
*   MongoDB (running locally on port 27017 or accessible via URL)
*   A Gemini API Key (obtained from [Google AI Studio](https://aistudio.google.com/))

---

## Installation & Setup

1.  **Clone / Copy the codebase to your target directory.**

2.  **Install dependencies**:
    Using `pip`:
    ```bash
    pip install -e .
    # Or install manually:
    pip install fastapi uvicorn beanie motor google-adk google-genai pydantic pydantic-settings python-dotenv
    ```

3.  **Configure environment variables**:
    Create a `.env` file in the project root:
    ```env
    # MongoDB URL
    MONGODB_URL=mongodb://localhost:27017/market_insights
    PORT=8000
    HOST=0.0.0.0

    # Gemini API Key from Google AI Studio
    GEMINI_API_KEY=your_actual_gemini_api_key_here
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    ```

---

## Running the Application

Start the local development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running, navigate to:
*   **Interactive Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **API Root status check**: [http://localhost:8000/](http://localhost:8000/)

---

## API Endpoints

### 1. Trigger competitor analysis
*   **HTTP Method**: `POST`
*   **URL Path**: `/api/v1/insights`
*   **Request Body**:
    ```json
    {
      "competitor": "https://notion.so"
    }
    ```
    *Note: The input is checked automatically. If it's a domain/URL it is treated as a website; otherwise, it is treated as a product name (e.g. `"Slack"`).*
*   **Response (202 Accepted)**:
    ```json
    {
      "id": "645d1f8fb8ec63a24db90d9a",
      "competitor": "https://notion.so",
      "is_website": true,
      "status": "PENDING",
      "price_insights": null,
      "sentiment_insights": null,
      "marketing_insights": null,
      "error_message": null,
      "created_at": "2026-05-24T12:00:00Z",
      "updated_at": "2026-05-24T12:00:00Z"
    }
    ```

### 2. Get competitor analysis details
*   **HTTP Method**: `GET`
*   **URL Path**: `/api/v1/insights/{insight_id}`
*   **Response (200 OK)**:
    Returns the updated status (`PENDING`, `COMPLETED`, or `FAILED`) along with the synthesized analyst reports:
    ```json
    {
      "id": "645d1f8fb8ec63a24db90d9a",
      "competitor": "https://notion.so",
      "is_website": true,
      "status": "COMPLETED",
      "price_insights": "Notion has a free tier for individuals...",
      "sentiment_insights": "Users love Notion's flexibility but note performance lag...",
      "marketing_insights": "Notion targets small-to-medium businesses and remote teams...",
      "error_message": null,
      "created_at": "2026-05-24T12:00:00Z",
      "updated_at": "2026-05-24T12:00:15Z"
    }
    ```

### 3. List all competitor analysis tasks
*   **HTTP Method**: `GET`
*   **URL Path**: `/api/v1/insights`
*   **Response (200 OK)**:
    ```json
    [
      {
        "id": "645d1f8fb8ec63a24db90d9a",
        "competitor": "https://notion.so",
        "is_website": true,
        "status": "COMPLETED",
        "created_at": "2026-05-24T12:00:00Z"
      }
    ]
    ```
