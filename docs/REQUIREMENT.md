# **Mini Workflow Automation Engine — Requirement Document**

**Project Level**: Senior Full-Stack Developer (Prototype)
**Stack**: React 18+ (TypeScript) + React Flow (v11+) | FastAPI 3.11+ | SQLite / JSON
**Time Budget**: 4–6 hours

## **1️⃣ Overview**

Build a **simplified workflow automation tool** inspired by n8n/Zapier.
Users visually compose workflows as **Directed Acyclic Graphs (DAGs)** of **Python code nodes** on a drag-and-drop canvas.

- Each node executes **user-written Python code** in a sandboxed subprocess.
- Nodes have **named inputs and outputs**, allowing **conditional branching**.
- Trigger nodes start workflows; code nodes process data; router nodes branch based on output.

## **2️⃣ Functional Requirements**

### **2.1 Frontend (React + React Flow)**

- **Workflow Canvas**:
    - Add nodes: **Trigger Node**, **Code Node** (and optionally Router Node)
    - Connect nodes via **edges** (output → input)
    - Node configuration panel:
        - Node name / label
        - Python code (Monaco / CodeMirror)
        - Declared **input names** (e.g., `data`, `config`)
        - Declared **output names** (e.g., `pass`, `fail`)

    - Delete nodes and edges
    - Save workflow JSON to backend
    - Run workflow and display **execution results**

- **Run Visualization**:
    - Color-code nodes:
        - Green = success
        - Red = error
        - Gray = skipped / not triggered

    - Show **per-node outputs** and **execution duration** in side panel

### **2.2 Backend (FastAPI)**

#### **API Endpoints**

| Method | Endpoint                            | Description                                |
| ------ | ----------------------------------- | ------------------------------------------ |
| POST   | `/api/workflows`                    | Save workflow (nodes, edges, code, config) |
| GET    | `/api/workflows/{id}`               | Load workflow definition                   |
| POST   | `/api/workflows/{id}/run`           | Execute workflow, return results           |
| GET    | `/api/workflows/{id}/runs/{run_id}` | Fetch execution results                    |

#### **Execution Engine Requirements**

- Load workflow nodes, edges, code, and config
- **Validate DAG** (no cycles) at **save time**
- Build **adjacency list** and **topological order** at run-time
- Execute each node in **sandboxed Python subprocess**
    - Per-node timeout (default 5 seconds)
    - Capture stdout and stderr
    - Return outputs as JSON

- **Conditional branching**:
    - Output keys with `None` → downstream edge not triggered
    - Node executes only when **all connected inputs** are available

- Track per-node results:
    - Status: `success | error | skipped`
    - Outputs
    - Duration
    - Error messages

## **3️⃣ Data Models (Backend)**

### **NodeModel**

```python
id: str
type: str  # "trigger" | "code"
name: str
inputs: List[str]
outputs: List[str]
code: Optional[str]
config: Optional[dict]  # e.g., trigger payload, timeout
```

### **EdgeModel**

```python
source_node_id: str
source_output: str
target_node_id: str
target_input: str
```

### **WorkflowModel**

```python
id: str
name: str
nodes: List[NodeModel]
edges: List[EdgeModel]
```

### **NodeExecutionResult**

```python
node_id: str
status: str  # "success" | "error" | "skipped"
outputs: dict
error: Optional[str]
duration: float
```

### **WorkflowRunResult**

```python
run_id: str
workflow_id: str
node_results: List[NodeExecutionResult]
```

## **4️⃣ Architecture & Execution Flow**

### **4.1 High-Level Flow**

```text
[Trigger Node] --> [Code Node A] --> [Router Node] --> [Code Node B or C] --> [Code Node D]

Frontend:
- Creates nodes/edges
- Sends workflow JSON
- Displays execution results (node colors + outputs)

Backend:
1. Save workflow:
   - Validate schema
   - Detect cycles
   - Save to DB
2. Run workflow:
   - Load workflow JSON
   - Build adjacency list
   - Topologically sort nodes
   - Execute nodes in order
   - Handle branching and skipped nodes
   - Return execution report
```

### **4.2 Trigger vs Router**

- **Trigger Node**:
    - Entry point (manual API call / cron / webhook)
    - No inputs
    - Emits `payload` output

- **Router Node**:
    - Code node with multiple outputs
    - Output determines which downstream nodes execute
    - Not special — just a code node with multiple outputs

## **5️⃣ Sandboxed Python Execution**

- Each **code node** runs in a **subprocess**:
    - Wrap `execute(inputs: dict) -> dict` function
    - Inputs passed as JSON
    - Outputs returned as JSON

- Timeouts enforced (default 5s)
- Failures captured per node (error field)
- Prevents backend crash from user code

## **6️⃣ Decisions / Tradeoffs Made**

- **Cycle validation**: On save (frontend sees errors immediately)
- **Topological sort**: On run (supports dynamic branching, parallel execution)
- **Persistence**: JSON or SQLite (simple, lightweight)
- **Sandboxing**: Subprocess + exec (simple prototype)
    - Production alternative: `RestrictedPython` or Docker container per node

- **Parallel execution**: Not implemented (future improvement)
- **Frontend complexity**: Keep UI functional, use React Flow + basic styling
- **Node types**: Trigger, Code, Router (Router = multi-output code node)

## **7️⃣ Explicit Non-Goals**

- Multi-user / authentication
- Workflow versioning
- Drag-to-reorder nodes in canvas
- Real-time streaming of execution progress (polling only)
- Beautified UI (Tailwind defaults are fine)
- Full test coverage (prototype only)

## **8️⃣ Acceptance Criteria**

1. **Workflow Creation & Persistence**
    - Can create workflow with ≥3 nodes
    - Can save workflow JSON to backend
    - Backend rejects cyclic workflows

2. **Execution Engine**
    - Executes workflow DAG topologically
    - Trigger node starts workflow
    - Conditional outputs determine which nodes run
    - Timeout or errors in a node mark node as `error` but do not crash server
    - Skipped nodes reported correctly

3. **Frontend Visualization**
    - Node colors reflect status: green, red, gray
    - Node outputs shown in side panel
    - Workflow run report returned as JSON

4. **Demo Scenario**
    - Trigger Node emits `{ "score": 75 }`
    - Router Node branches:
        - `pass` → Output Node A (green)
        - `fail` → Output Node B (skipped / gray)

    - Matches expected conditional branching
