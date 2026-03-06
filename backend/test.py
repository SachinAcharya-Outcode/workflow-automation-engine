import asyncio
import uuid

from backend.engine import execute_workflow
from backend.models import EdgeModel, NodeModel, WorkflowModel


async def test_engine():
    workflow = WorkflowModel(
        id="workflow-1",
        name="Test Workflow",
        nodes=[
            NodeModel(
                id="node-1",
                type="trigger",
                name="Trigger",
                outputs=["data"],
                config={"payload": {"score": 75}},
            ),
            NodeModel(
                id="node-2",
                type="code",
                name="Router",
                inputs=["data"],
                outputs=["pass", "fail"],
                code="""
def execute(inputs):
    data = inputs.get("data", {})
    if data.get("score", 0) > 50:
        return {"pass": data, "fail": None}
    else:
        return {"pass": None, "fail": data}
""",
            ),
            NodeModel(
                id="node-3",
                type="code",
                name="Output A",
                inputs=["pass"],
                outputs=["message"],
                code="""
def execute(inputs):
    return {"message": "Passed!"}
""",
            ),
            NodeModel(
                id="node-4",
                type="code",
                name="Output B",
                inputs=["fail"],
                outputs=["message"],
                code="""
def execute(inputs):
    return {"message": "Failed!"}
""",
            ),
        ],
        edges=[
            EdgeModel(
                source_node_id="node-1",
                source_output="data",
                target_node_id="node-2",
                target_input="data",
            ),
            EdgeModel(
                source_node_id="node-2",
                source_output="pass",
                target_node_id="node-3",
                target_input="pass",
            ),
            EdgeModel(
                source_node_id="node-2",
                source_output="fail",
                target_node_id="node-4",
                target_input="fail",
            ),
        ],
    )

    result = await execute_workflow(workflow, str(uuid.uuid4()))
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(test_engine())
