# LangFlow — Visual Travel Planner Workflow

This folder recreates the multi-agent workflow in **LangFlow**, the visual
dataflow builder. It reuses the *exact same agents* as the FastAPI/LangGraph
app — the LangFlow components are thin wrappers, just like the LangGraph nodes.

## Files

| File | What it is |
|---|---|
| `langflow_components/*.py` | One LangFlow Custom Component per agent (Planner, Flight, Hotel, Weather, Budget, Final Response) |
| `travel_planner_flow.json` | The flow graph: nodes + edges + canvas layout |

## The graph

```
                    ┌─► Flight ──┐
Planner ─(trip)─────┼─► Hotel  ──┼─► Budget ─► Final Response ─► (JSON + Text)
                    └─► Weather ─────────────────┘
```

Planner emits the `trip`; Flight/Hotel/Weather each consume it; Budget joins
Flight+Hotel; Final Response consumes everything.

## How LangFlow maps to the code

| LangFlow concept | Our code | Notes |
|---|---|---|
| **Component (node)** | `*AgentComponent` wrapping `build_*_agent_from_settings()` | Same role as a **LangGraph node** — a thin adapter over the agent. The agents are unchanged. |
| **Component input port** | a `DataInput` / `MessageTextInput` | Maps to a field the node reads — e.g. Budget's `flights`/`hotel`. |
| **Component output port** | an `Output(method=...)` returning `Data`/`Message` | The value written for downstream nodes. |
| **Edge** | data passed between nodes | Equivalent to a **TravelState channel** being read by the next node. |
| **The canvas / flow** | the compiled `StateGraph` in `app/agents/graph/workflow.py` | The whole orchestration. |
| **`Data` object** | a Pydantic model serialized to a dict (`model_dump()`) | Components pass dicts and rebuild Pydantic models (`TripParameters(**data)`). |
| **Optional input (`required=False`)** | the **conditional skip** (`route_after_planner`) | A node still runs if an optional upstream is absent — same effect as skipping Flight/Hotel/Weather. |

### LangGraph vs LangFlow — the one real difference

- **LangGraph is control-flow**: edges define *execution order*; Budget has a
  real **join/barrier** (waits for Flight, Hotel and Weather) and Weather routes
  *through* Budget to Final.
- **LangFlow is dataflow**: edges define *data dependencies*. Weather connects
  **directly to Final** (Budget doesn't use weather), and each node runs when
  its inputs are ready. Same agents, same result — the wiring reflects "who
  needs whose data" rather than "what runs after what".

## Running it

```bash
pip install langflow                       # heavy; use a separate venv
export LANGFLOW_COMPONENTS_PATH="$(pwd)/flows/langflow_components"
export PYTHONPATH="$(pwd)"                  # so `app` is importable
# (set the same .env vars the app uses: LLM provider/keys, etc.)
langflow run
```

Then in the UI: the six agents appear under **Custom Components**. Either
**import** `travel_planner_flow.json` or drag the components onto the canvas and
wire them per the graph above. Press **Play** on the Final Response node to run
the whole pipeline; the Planner's text input is the trip request.

> Note: LangFlow's export schema is version-specific. `travel_planner_flow.json`
> captures the canonical topology (nodes, ports, edges, layout); on import,
> LangFlow may re-encode handle IDs. The components in `langflow_components/`
> are the durable, runnable artifacts.
