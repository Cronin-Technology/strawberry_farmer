import requests
import json
import random

# --- Simulated Sensor Readings ---
def read_sensors():
    temperature = round(random.uniform(16, 28), 1)
    humidity = round(random.uniform(45, 85), 1)
    return temperature, humidity


# --- Simple Retrieval Function ---
def retrieve_context(query):
    with open("strawberry.txt", "r") as f:
        text = f.read()

    # naive retrieval (keyword match)
    relevant_lines = []
    for line in text.split("\n"):
        if any(word in line.lower() for word in ["temperature", "humidity"]):
            relevant_lines.append(line)

    return "\n".join(relevant_lines)


# --- Call Granite via Ollama REST API ---
def query_granite(prompt):
    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "granite4:350m",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]


# --- Main Control Logic ---
def greenhouse_controller():
    temp, hum = read_sensors()

    context = retrieve_context("strawberry temperature humidity")

    prompt = f"""
You are a greenhouse control assistant.

Sensor readings:
Temperature: {temp} C
Humidity: {hum} %

Reference cultivation guide:
{context}

Based only on the reference guide,
recommend actions in JSON format:

{{
  "increase_heat": true/false,
  "increase_ventilation": true/false,
  "activate_dehumidifier": true/false,
  "activate_shading": true/false,
  "reason": "short technical explanation"
}}
"""

    result = query_granite(prompt)
    print("Sensor Data:", temp, "C,", hum, "%")
    print("Granite Recommendation:")
    print(result)


if __name__ == "__main__":
    greenhouse_controller()

