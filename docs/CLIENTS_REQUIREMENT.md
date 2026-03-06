# Senior Full-Stack Developer Test Task

## FlowForge — A Mini Workflow Automation Engine

**Stack:** React \+ React Flow (frontend) · FastAPI \+ Python (backend) **Time Budget:** 4–6 hours **Level:** Senior Full-Stack Developer

---

## Overview

Build a simplified workflow automation tool inspired by n8n/Zapier. Users visually compose workflows as directed graphs of **Python code nodes** using a drag-and-drop canvas. Each node executes user-written Python in a sandboxed subprocess on the backend, supports multiple named inputs/outputs, and can route data conditionally.

The deliverable is a single working application — not production-grade, but demonstrating strong architecture decisions, clean code, and pragmatic tradeoffs under time pressure.

---

## Functional Requirements

### 1\. Workflow Canvas (React \+ React Flow)

- A visual node-graph editor where users can:
    - **Add nodes** from a sidebar or context menu (at minimum: Code Node, Trigger Node)
    - **Connect nodes** via edges between named input/output handles
    - **Configure each node** in a side panel or modal with:
        - Node name / label
        - Python code (use a code editor component — Monaco or CodeMirror)
        - Declared **input names** (e.g. `data`, `config`) and **output names** (e.g. `result`, `error`, `branch_a`, `branch_b`)
    - **Delete** nodes and edges
    - **Save** the workflow (persist to backend)
    - **Execute** the full workflow with a "Run" button

### 2\. Node Execution Model

Each Code Node receives a Python function skeleton:

```
def execute(inputs: dict) \-\> dict:

    """

    inputs: { "input\_name": \<value from connected upstream node output\> }

    return: { "output\_name": \<value to send downstream\>, ... }



    Only the keys matching declared output names are forwarded.

    Missing keys \= that output branch is not triggered (enables conditionals).

    """

    data \= inputs.get("data", {})



    if data.get("score", 0\) \> 50:

        return {"pass": data, "fail": None}

    else:

        return {"pass": None, "fail": data}
```

**Key rules:**

- If a returned output value is `None`, the downstream edge from that output is **not triggered** — this is how conditional branching works.
- A node executes only when **all** connected inputs have received a value (barrier/join semantics).
- The **Trigger Node** is a special no-input node that kicks off the workflow. It should accept a static JSON payload the user can configure, which it emits as its single output.

### 3\. Backend Workflow Engine (FastAPI)

Implement the following API surface:

| Method | Endpoint                            | Description                                           |
| :----- | :---------------------------------- | :---------------------------------------------------- |
| `POST` | `/api/workflows`                    | Create/save a workflow (nodes, edges, code, metadata) |
| `GET`  | `/api/workflows/{id}`               | Load a workflow                                       |
| `POST` | `/api/workflows/{id}/run`           | Execute a workflow, return results                    |
| `GET`  | `/api/workflows/{id}/runs/{run_id}` | Get execution results / status                        |

**Execution engine requirements:**

- Resolve the graph into a **topological execution order**
- Execute each node's Python code in a **sandboxed subprocess** (use `subprocess` with `exec()` in a restricted child process, or `RestrictedPython`, or a Docker-based approach — document your choice and tradeoffs)
- Enforce a **per-node timeout** (e.g. 5 seconds)
- Collect per-node execution results: status (`success` | `error` | `skipped`), output data, stderr, duration
- Return a full **run report** with per-node results so the frontend can visualize them

### 4\. Run Visualization

After execution completes:

- Color-code nodes on the canvas: **green** (success), **red** (error), **gray** (skipped/not triggered)
- Show per-node output data and errors in the side panel when a node is selected
- Show execution duration per node

---

## Non-Functional Requirements

- **State management:** Use Zustand, Jotai, or React context — justify your choice briefly in the README
- **Persistence:** SQLite via SQLAlchemy (or even a JSON file store) — keep it simple
- **Error handling:** The app should never crash on bad user code — sandbox failures should surface as node errors in the run report
- **Type safety:** Use Pydantic models on the backend; TypeScript on the frontend
- **Code quality:** Consistent formatting, meaningful names, no dead code. We value readability over cleverness.

---

## Evaluation Criteria

| Area                      | Weight | What We Look For                                                                            |
| :------------------------ | :----- | :------------------------------------------------------------------------------------------ |
| **Architecture & Design** | 30%    | Clean separation of concerns, sensible data models, graph execution logic, sandbox strategy |
| **Frontend Quality**      | 25%    | React Flow integration, responsive UX, state management, TypeScript usage                   |
| **Backend Quality**       | 25%    | API design, Pydantic models, execution engine correctness, error handling                   |
| **Pragmatic Tradeoffs**   | 10%    | Evidence of time management — what you built vs. what you intentionally deferred            |
| **Documentation**         | 10%    | Clear README with setup instructions, architecture notes, and a "What I'd improve" section  |

---

## Deliverables

1. **Git repository** with a clear commit history (we want to see how you work, not a single squashed commit)
2. **README.md** containing:
    - Setup & run instructions (ideally `docker-compose up` or two terminal commands)
    - Architecture overview (a short paragraph \+ optional diagram)
    - Key design decisions and tradeoffs
    - "What I'd do with more time" section
3. **Working application** that can:
    - Create a workflow with 3+ nodes
    - Execute it and display per-node results
    - Handle at least one branching/conditional scenario

---

## Starter Scenario (for your own testing)

Build this workflow to prove the system works:

\[Trigger\] \[Transform\] \[Output A\]

payload: {"score": 75} \--\> if score \> 50: \--\> print pass

                              return pass/fail

                                    \\

                                     \+--------\>  \[Output B\]

                                                  print fail

- **Trigger Node** — emits `{"score": 75}` on output `"data"`
- **Router Node** — reads `inputs["data"]`, branches to `"pass"` or `"fail"` output based on score
- **Output A** — receives from `"pass"`, returns `{"message": "Passed!"}`
- **Output B** — receives from `"fail"`, returns `{"message": "Failed!"}`

Expected result: Output A runs (green), Output B is skipped (gray).

---

## Explicit Non-Goals (don't spend time on these)

- Authentication / multi-user
- Workflow versioning
- Real-time streaming of execution progress (polling or post-hoc is fine)
- Drag-to-reorder nodes in a list
- Beautiful styling (functional and clean is enough; default shadcn/Tailwind is fine)
- Comprehensive test coverage (a couple of key unit tests for the execution engine are appreciated but not required)

---

## Tech Constraints

| Layer              | Required                       | Optional/Suggested       |
| :----------------- | :----------------------------- | :----------------------- |
| Frontend framework | React 18+ with TypeScript      | —                        |
| Graph editor       | React Flow (v11+)              | —                        |
| Code editor        | Monaco Editor or CodeMirror 6  | —                        |
| Backend framework  | FastAPI (Python 3.11+)         | —                        |
| Data validation    | Pydantic v2                    | —                        |
| Storage            | SQLite / JSON file             | SQLAlchemy               |
| Sandboxing         | subprocess \+ restricted exec  | RestrictedPython, Docker |
| Package manager    | npm/pnpm (FE), pip/poetry (BE) | —                        |

---

## Hints & Guidance

- **Start with the data model.** Define your `Workflow`, `Node`, `Edge`, and `RunResult` schemas first — everything flows from there.
- **Topological sort is the core algorithm.** Use Kahn's algorithm or DFS-based ordering. Handle cycle detection.
- **Keep sandbox simple.** A subprocess that `exec()`s the user code with a timeout is perfectly acceptable for this exercise. Document what a production approach would look like.
- **React Flow custom nodes** are powerful — a custom node component with dynamic handles based on declared inputs/outputs is the way to go.
- **Don't over-engineer.** A clean 80% solution beats a messy 100% solution every time.

---

_Good luck. We're excited to see how you think._
