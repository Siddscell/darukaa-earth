# Demo Walkthrough

## 1. Setup
Ensure both the frontend and backend servers are running.
- Backend: `uvicorn app.main:app --reload --port 8000`
- Frontend: `npm run dev` in the `frontend` folder.
- Ensure Ollama is running if testing the full LLM mode.

## 2. Load Semi-Arid Farm Scenario
1. Open `http://localhost:3000` in your browser.
2. On the home page or scenario selection screen, click the **"Try Semi-Arid Farm"** button to load a pre-configured environmental profile.

## 3. Run Analysis
1. Once the profile is loaded, click **"Analyze Biodiversity"**.
2. Alternatively, type a query in the chat box, such as "How can I improve soil moisture and biodiversity given my current metrics?"

## 4. Show Evidence Drawer
1. When the recommendations are returned, they will include citation badges.
2. Click on a citation badge (e.g., `[Source 1]`) to open the **Evidence Drawer**.
3. Show the detailed source information, confidence level, and original text chunk.

## 5. Show Reasoning Trace
1. Below the recommendations, click the **"How this was generated"** accordion.
2. Walk through the reasoning trace to show the system's thought process, including retrieved metrics, evaluated relationships, and trade-off considerations.

## 6. Test Structured JSON Input
1. Send a POST request to `/api/environment/profile` using Postman or cURL with a custom JSON payload representing a different biome.
2. Show how the UI or subsequent chat responses adapt to the new profile context.

## 7. Show System Status
1. Navigate to the system status indicator (usually in the header or footer).
2. Click it to view the backend connection status, ChromaDB status, and active LLM model.
