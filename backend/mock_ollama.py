from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

class GenerateRequest(BaseModel):
    model: str
    prompt: str
    stream: bool
    options: dict

@app.get("/api/tags")
def get_tags():
    return {
        "models": [
            {"name": "mistral:7b"}
        ]
    }

@app.post("/api/generate")
def generate(req: GenerateRequest):
    print(f"--- MOCK OLLAMA RECEIVED PROMPT ---\n{req.prompt.encode('utf-8', 'replace').decode('utf-8')}\n-----------------------------------".encode('ascii', 'replace').decode('ascii'))
    response_json = """{
  "summary_message": "Based on the evidence retrieved from agricultural studies in semi-arid regions, here is what you can do about your low soil organic carbon.",
  "recommendations": [
    {
      "title": "Adopt Conservation Tillage",
      "action": "Minimize soil disturbance by switching to no-till or reduced tillage.",
      "reasoning": "Reducing tillage helps preserve soil structure and allows organic matter to accumulate over time.",
      "impacted_metrics": ["soil_organic_carbon", "water_retention"],
      "time_horizon": "long-term",
      "confidence": "High",
      "evidence": [
        {
          "title": "State of the World's Soil Resources: Main Report",
          "source": "FAO",
          "year": 2015,
          "supporting_excerpt": "intensive cereal monocultures... consistently deplete soil organic carbon",
          "topic": "soil",
          "variables": ["organic_carbon"]
        }
      ]
    }
  ]
}"""
    return {"model": req.model, "response": response_json, "done": True}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=11434)
