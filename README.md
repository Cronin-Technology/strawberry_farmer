# Greenhouse Control Assistant

A minimal demo that pairs live (simulated) sensor readings with a small, locally-hosted language model to produce greenhouse control recommendations. Temperature and humidity are matched against a strawberry cultivation guide, and the [Granite](https://www.ibm.com/granite) model — served locally through [Ollama](https://ollama.com) — decides which actuators (heat, ventilation, dehumidifier, shading) should be engaged.

Everything runs on your own machine. No cloud API, no keys, no data leaving the box.

## How it works

The script (`simple_example.py`) runs a single control cycle in four steps:

1. **Read sensors** — `read_sensors()` generates a simulated temperature (16–28 °C) and relative humidity (45–85 %). In a real deployment you'd replace this with actual hardware reads.
2. **Retrieve context** — `retrieve_context()` opens `strawberry.txt` and pulls out any lines mentioning *temperature* or *humidity* via a naive keyword match. This is the lightweight "retrieval" step that grounds the model in your cultivation guide.
3. **Query the model** — the readings and retrieved guidance are assembled into a prompt and sent to Granite through Ollama's REST API (`query_granite()`).
4. **Report** — the model returns a JSON block of recommended actions with a short technical justification, which is printed to the console.

```
Sensors ──▶ Retrieval (strawberry.txt) ──▶ Prompt ──▶ Granite (via Ollama) ──▶ JSON recommendation
```

## Project files

| File | Purpose |
|------|---------|
| `simple_example.py` | Main control loop: read sensors, retrieve context, query the model, print result. |
| `strawberry.txt` | Cultivation guide used as the reference knowledge source. |

### The cultivation guide (`strawberry.txt`)

The reference thresholds the model is asked to reason over:

- Optimal daytime temperature: **20–24 °C**
- Optimal nighttime temperature: **15–18 °C**
- Relative humidity: **60–64 %**
- Humidity above 65 % → increase ventilation or activate dehumidifier
- Temperature above 26 °C → activate shading or ventilation

## Prerequisites

- **Python 3.8+**
- **`requests`** library — `pip install requests`
- **Ollama** — installed and running (see setup below)

## Setup

### 1. Install Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start the Ollama server

```bash
ollama serve
```

Leave this running in its own terminal (or as a background service). The script talks to it at `http://localhost:11434`.

### 3. Pull the Granite model

```bash
ollama pull granite4:350m
```

The `350m` build is a small, fast model well-suited to a lightweight local demo like this one.

### 4. Verify Ollama is running

```bash
curl http://localhost:11434
```

You should see a response reading:

```
Ollama is running
```

### 5. Install the Python dependency

```bash
pip install requests
```

## Running it

With Ollama serving and the model pulled, run the controller from the directory containing both `simple_example.py` and `strawberry.txt`:

```bash
python simple_example.py
```

### Example output

```
Sensor Data: 27.3 C, 71.2 %
Granite Recommendation:
{
  "increase_heat": false,
  "increase_ventilation": true,
  "activate_dehumidifier": true,
  "activate_shading": true,
  "reason": "Temperature exceeds 26 C and humidity is above 65%, so ventilation, shading, and dehumidification are recommended."
}
```

Because sensor values are randomized each run, the recommendation will vary from run to run.

## Configuration

A few things you may want to change, all near the top of the relevant functions in `simple_example.py`:

- **Model** — swap `granite4:350m` in `query_granite()` for any model you've pulled with `ollama pull`.
- **Ollama endpoint** — update the `url` in `query_granite()` if Ollama runs on a different host or port.
- **Sensor ranges** — adjust the bounds in `read_sensors()`, or replace the function entirely with real hardware reads.
- **Reference guide** — edit `strawberry.txt` (or point `retrieve_context()` at a different file) to control what the model reasons over.

## Notes and caveats

- **Retrieval is intentionally naive.** It's a simple keyword match, fine for a short single-file guide. For larger or more varied documents you'd want proper chunking and embeddings-based retrieval.
- **No response validation.** The script prints whatever the model returns. Small models don't always produce strictly valid JSON, so if you build on this, parse and validate the output (e.g. `json.loads`) and handle failures.
- **No error handling on the API call.** If Ollama isn't running, the `requests.post` call will fail. Make sure `ollama serve` is up before running.
- **Single cycle.** The controller runs once and exits. Wrap `greenhouse_controller()` in a loop with a delay if you want continuous monitoring.

## License

Add your preferred license here.
