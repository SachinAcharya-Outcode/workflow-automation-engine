# **FlowForge 6-Node Workflow Diagram**

```text
Legend:
[Node] - Node Type (Trigger / Code / Router)
→       - Edge (data flow)
{data}  - Example output from node
(Green/Red/Gray) - Execution status

+-------------------+
| [Trigger_1]       |  <-- Emits payload {"score": 75}
| Type: Trigger     |
+-------------------+
          |
          v
+-------------------+
| [Code_A]          |  <-- Simple transform node
| Type: Code        |
| Inputs: data      |
| Outputs: pass, fail|
+-------------------+
          |
          v
+-------------------+
| [Router_1]        |  <-- Branch based on "score"
| Type: Code/Router |
| Inputs: data      |
| Outputs: pass, fail|
+--------+----------+
         |
         v
+-------------------+      +-------------------+
| [Output_A]        |      | [Output_B]        |
| Type: Code        |      | Type: Code        |
| Inputs: pass      |      | Inputs: fail      |
| Outputs: message  |      | Outputs: message  |
+-------------------+      +-------------------+
         |                       |
     (Green)                  (Gray)
         |                       |
         v                       v
+-------------------+
| [Code_D]          | <-- Optional next node using Output_A
| Type: Code        |
| Inputs: message   |
| Outputs: final    |
+-------------------+
```

---

## **Explanation of Flow**

1. **Trigger_1**: Entry node → emits payload `{ "score": 75 }`.
    - Status: Green (success)

2. **Code_A**: Processes data → outputs `pass` or `fail` based on `score`.
    - Example code:

```python
def execute(inputs):
    data = inputs.get("data", {})
    if data.get("score", 0) > 50:
        return {"pass": data, "fail": None}
    return {"pass": None, "fail": data}
```

3. **Router_1**: Reads outputs `pass/fail` → routes to **Output_A** or **Output_B**.
    - Only edges with non-None outputs are triggered

4. **Output_A / Output_B**: Final nodes showing messages:
    - Output_A: `{"message": "Passed!"}` → Green (executed)
    - Output_B: Skipped → Gray (not triggered)

5. **Code_D**: Optional next node that takes Output_A’s result → can process further

---

## **Execution Logs Simulation**

| Node      | Status  | Output                                |
| --------- | ------- | ------------------------------------- |
| Trigger_1 | Success | {"score": 75}                         |
| Code_A    | Success | {"pass": {"score": 75}, "fail": None} |
| Router_1  | Success | {"pass": {"score": 75}, "fail": None} |
| Output_A  | Success | {"message": "Passed!"}                |
| Output_B  | Skipped | None                                  |
| Code_D    | Success | {"final": "Passed processed"}         |

---

## **Key Notes**

- **Skipped nodes**: Any node that receives no valid inputs (all edges are None) is skipped → Gray in UI
- **Branching**: Router nodes are just code nodes with multiple outputs
- **Execution order**: Determined dynamically at runtime using **topological sort + ready queue**
- **Parallelism**: Nodes at same level without dependencies could be executed in parallel (future improvement)

---

### ✅ **Why This Diagram Helps**

- Shows **entry → transform → router → multiple outputs → next nodes**
- Clarifies **branching logic and skipped nodes**
- Maps directly to **data models**:
    - `[Node]` → NodeModel
    - `Edge → node connections` → EdgeModel

- Can be used for **frontend development**, **AI agents**, or **documentation**
