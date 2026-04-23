# import uuid
# import logging
# import threading
# from fastapi import APIRouter, BackgroundTasks, HTTPException

# from api.models import (
#     TaskCreateRequest,
#     TaskResponse,
#     TaskStatusResponse,
#     TaskResultResponse,
#     SessionSummaryResponse,
# )
# from api.session_store import create_session, get_session, update_session, list_sessions, delete_session, delete_all_sessions
# from core.orchestrator import OrchestratorGraph

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api/v1/task", tags=["tasks"])

# # Track running tasks with their state
# _task_states = {}


# def _set_task_state(session_id: str, agent: str, step: int, total_steps: int = 4):
#     _task_states[session_id] = {
#         "agent": agent,
#         "step": step,
#         "total_steps": total_steps,
#     }


# def run_task_async(session_id: str, goal: str, config: dict):
#     """Launch task execution without blocking the background task worker."""
#     try:
#         update_session(session_id, {"status": "running"})
#         _set_task_state(session_id, "decompose_goal", 1)

#         thread = threading.Thread(
#             target=_execute_task,
#             args=(session_id, goal, config),
#             daemon=True,
#         )
#         thread.start()

#     except Exception as e:
#         logger.exception("Task execution failed")
#         update_session(session_id, {
#             "status": "failed",
#             "result": f"Error: {str(e)}"
#         })


# def _execute_task(session_id: str, goal: str, config: dict):
#     """Execute graph with basic state tracking."""
#     try:
#         graph = OrchestratorGraph(
#             config=config or {},
#             status_callback=lambda agent, step: _set_task_state(session_id, agent, step),
#         )
#         result = graph.run(goal=goal, config=config or {}, session_id=session_id)

#         final_output = result.get("final_output", "")
#         errors = result.get("error_log", [])
#         final_status = "completed"

#         if not final_output and errors:
#             final_output = "Task failed:\n" + "\n".join(errors)
#             final_status = "failed"

#         update_session(session_id, {
#             "status": final_status,
#             "result": final_output
#         })

#         _task_states.pop(session_id, None)

#     except Exception as e:
#         logger.exception(f"Graph execution failed: {e}")
#         update_session(session_id, {
#             "status": "failed",
#             "result": str(e)
#         })
#         _task_states.pop(session_id, None)


# @router.post("/create", response_model=TaskResponse)
# async def create_task(req: TaskCreateRequest, background_tasks: BackgroundTasks):
#     session_id = req.session_id or str(uuid.uuid4())
#     config = dict(req.config or {})

#     if req.llm_provider:
#         config["llm_provider"] = req.llm_provider
#     if req.output_format:
#         config["output_format"] = req.output_format

#     try:
#         create_session(session_id, req.goal, config)

#         background_tasks.add_task(
#             run_task_async,
#             session_id,
#             req.goal,
#             config
#         )

#         return TaskResponse(
#             task_id=session_id,
#             session_id=session_id,
#             status="started"
#         )

#     except Exception:
#         logger.exception("Failed to create task")
#         raise HTTPException(status_code=500, detail="Task creation failed")


# @router.get("/{task_id}/status", response_model=TaskStatusResponse)
# async def get_status(task_id: str):
#     session = get_session(task_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Task not found")

#     # Get current agent from task state
#     task_state = _task_states.get(task_id, {})
#     agent = task_state.get("agent", "unknown")
#     step = task_state.get("step", 0)
#     total_steps = max(task_state.get("total_steps", 4), 1)
#     progress = min(step / total_steps, 1.0) if session.status == "running" else (1.0 if session.status == "completed" else 0.0)

#     return TaskStatusResponse(
#         status=session.status,
#         progress=progress,
#         current_agent=agent,
#         logs=[f"Step {step}: {agent}"]
#     )


# @router.get("/{task_id}/result", response_model=TaskResultResponse)
# async def get_result(task_id: str):
#     session = get_session(task_id)
#     if not session:
#         raise HTTPException(status_code=404, detail="Task not found")

#     if session.status != "completed":
#         raise HTTPException(status_code=400, detail="Task not completed yet")

#     return TaskResultResponse(
#         output=session.result,
#         agent_trace=None,
#         sources=None,
#         created_at=session.created_at.isoformat()
#     )


# @router.get("/sessions", response_model=list[SessionSummaryResponse])
# async def get_sessions():
#     sessions = list_sessions()
#     return [
#         SessionSummaryResponse(
#             session_id=session.id,
#             goal=session.goal,
#             status=session.status,
#             created_at=session.created_at.isoformat(),
#         )
#         for session in sessions
#     ]

# @router.delete("/sessions")
# async def delete_all_sessions_endpoint():
#     """Delete all sessions from the database."""
#     success = delete_all_sessions()
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to delete all sessions")
#     return {"message": "All sessions deleted successfully"}

# @router.delete("/{task_id}")
# async def delete_single_session_endpoint(task_id: str):
#     """Delete a specific session by ID."""
#     success = delete_session(task_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Task not found or could not be deleted")
    
#     # Clean up tracking dictionary if it's currently running
#     _task_states.pop(task_id, None)
    
#     return {"message": f"Session {task_id} deleted successfully"}


import uuid
import logging
import threading
from fastapi import APIRouter, BackgroundTasks, HTTPException

from api.models import (
    TaskCreateRequest,
    TaskResponse,
    TaskStatusResponse,
    TaskResultResponse,
    SessionSummaryResponse,
)
from api.session_store import create_session, get_session, update_session, list_sessions, delete_session, delete_all_sessions
from core.orchestrator import OrchestratorGraph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/task", tags=["tasks"])

# Track current agent + full history
_task_states = {}


def _set_task_state(session_id: str, agent: str, step: int, total_steps: int = 4):
    existing = _task_states.get(session_id, {})
    history: list = existing.get("history", [])

    if not history or history[-1] != agent:
        history.append(agent)

    _task_states[session_id] = {
        "agent":       agent,
        "step":        step,
        "total_steps": total_steps,
        "history":     history,
        "done":        False,
    }


def run_task_async(session_id: str, goal: str, config: dict):
    try:
        update_session(session_id, {"status": "running"})
        _set_task_state(session_id, "decompose_goal", 1)

        thread = threading.Thread(
            target=_execute_task,
            args=(session_id, goal, config),
            daemon=True,
        )
        thread.start()

    except Exception as e:
        logger.exception("Task launch failed")
        update_session(session_id, {"status": "failed", "result": f"Error: {str(e)}"})


def _execute_task(session_id: str, goal: str, config: dict):
    try:
        graph = OrchestratorGraph(
            config=config or {},
            status_callback=lambda agent, step: _set_task_state(session_id, agent, step),
        )
        result = graph.run(goal=goal, config=config or {}, session_id=session_id)

        final_output = result.get("final_output", "")
        errors       = result.get("error_log", [])
        final_status = "completed"

        if not final_output and errors:
            final_output = "Task failed:\n" + "\n".join(errors)
            final_status = "failed"

        # ✅ result["tasks"] se definitive history banao — timing issue fix
        # Callback pe depend nahi — actual completed tasks se agents nikalo
        completed_agents = [
            t.get("agent_type", "") + "_node"
            for t in result.get("tasks", [])
            if t.get("status") == "completed"
        ]
        full_history = ["decompose_goal"] + completed_agents + ["synthesize"]

        _task_states[session_id] = {
            "agent":       "synthesize",
            "step":        4,
            "total_steps": 4,
            "history":     full_history,
            "done":        True,
        }

        update_session(session_id, {
            "status": final_status,
            "result": final_output,
        })

    except Exception as e:
        logger.exception(f"Graph execution failed: {e}")

        existing_history = _task_states.get(session_id, {}).get("history", [])
        _task_states[session_id] = {
            "agent":       "failed",
            "step":        0,
            "total_steps": 4,
            "history":     existing_history,
            "done":        True,
        }

        update_session(session_id, {
            "status": "failed",
            "result": str(e),
        })


@router.post("/create", response_model=TaskResponse)
async def create_task(req: TaskCreateRequest, background_tasks: BackgroundTasks):
    session_id = req.session_id or str(uuid.uuid4())
    config = dict(req.config or {})

    if req.llm_provider:
        config["llm_provider"] = req.llm_provider
    if req.output_format:
        config["output_format"] = req.output_format

    try:
        create_session(session_id, req.goal, config)
        background_tasks.add_task(run_task_async, session_id, req.goal, config)
        return TaskResponse(task_id=session_id, session_id=session_id, status="started")

    except Exception:
        logger.exception("Failed to create task")
        raise HTTPException(status_code=500, detail="Task creation failed")


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
async def get_status(task_id: str):
    session = get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    task_state  = _task_states.get(task_id, {})
    agent       = task_state.get("agent", "unknown")
    step        = task_state.get("step", 0)
    total_steps = max(task_state.get("total_steps", 4), 1)
    history     = task_state.get("history", [])

    # Progress
    if session.status == "completed":
        progress = 1.0
    elif session.status == "running":
        progress = min(step / total_steps, 0.95)
    else:
        progress = 0.0

    # ✅ Logs — completed task mein full history, running mein current highlighted
    if session.status == "completed":
        logs = [f"✓ {a}" for a in history]
    elif session.status == "running":
        completed_part = history[:-1]
        current_part   = history[-1] if history else agent
        logs = [f"✓ {a}" for a in completed_part] + [f"⟳ {current_part}"]
    else:
        logs = [f"✗ {agent}"] if agent != "unknown" else []

    return TaskStatusResponse(
        status=session.status,
        progress=progress,
        current_agent=agent,
        logs=logs,
    )


@router.get("/{task_id}/result", response_model=TaskResultResponse)
async def get_result(task_id: str):
    session = get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Task not found")

    if session.status != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")

    return TaskResultResponse(
        output=session.result,
        agent_trace=None,
        sources=None,
        created_at=session.created_at.isoformat()
    )


@router.get("/sessions", response_model=list[SessionSummaryResponse])
async def get_sessions():
    sessions = list_sessions()
    return [
        SessionSummaryResponse(
            session_id=s.id,
            goal=s.goal,
            status=s.status,
            created_at=s.created_at.isoformat(),
        )
        for s in sessions
    ]


@router.delete("/sessions")
async def delete_all_sessions_endpoint():
    success = delete_all_sessions()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete all sessions")
    return {"message": "All sessions deleted successfully"}


@router.delete("/{task_id}")
async def delete_single_session_endpoint(task_id: str):
    success = delete_session(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or could not be deleted")
    _task_states.pop(task_id, None)
    return {"message": f"Session {task_id} deleted successfully"}