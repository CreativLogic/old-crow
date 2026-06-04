"""
CLI routes — Dedicated endpoint for terminal-based agent interaction.
Used by the `raven` CLI command and RAVEN's built-in terminal.
"""

import asyncio
import json
import logging
import os
import uuid

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

# Persistent CLI session — reused across CLI calls so context builds
_CLI_SESSION_ID = "cli-terminal"


def setup_cli_routes(
    session_manager,
    session_config,
    webhook_manager=None,
) -> APIRouter:
    router = APIRouter(prefix="/api/cli", tags=["cli"])

    @router.post("/chat")
    async def cli_chat(request: Request):
        """
        CLI-friendly chat endpoint. Accepts JSON, creates/uses a persistent
        CLI session, runs the agent, and streams NDJSON responses.

        Body: {"message": "...", "model": "deepseek-chat"}
        """
        body = await request.json()
        message = body.get("message", "").strip()
        model = body.get("model")

        if not message:
            raise HTTPException(400, "message is required")

        # Get or create the CLI session
        try:
            sess = session_manager.get_session(_CLI_SESSION_ID)
        except KeyError:
            sess = session_manager.create_session(
                session_id=_CLI_SESSION_ID,
                owner=getattr(request.state, "current_user", "cli"),
                name="CLI Terminal",
            )

        # Set model if specified
        if model:
            sess.model = model
            session_manager.save_session(sess)

        # Ensure a model is set
        if not getattr(sess, "model", "").strip():
            # Try to find a default
            from core.database import SessionLocal
            db = SessionLocal()
            try:
                row = db.execute(
                    "SELECT model FROM model_endpoints WHERE enabled = 1 LIMIT 1"
                ).fetchone()
                if row:
                    sess.model = row[0]
                    session_manager.save_session(sess)
            finally:
                db.close()

        if not getattr(sess, "model", "").strip():
            raise HTTPException(
                400,
                "No model configured. Open RAVEN and add a model endpoint first.",
            )

        # Run the agent and stream
        async def event_stream():
            try:
                from src.agent_loop import run_agent_loop
                from starlette.responses import StreamingResponse

                # Build a pseudo-request for the agent loop
                # The agent loop needs the session and message
                result_chunks = []

                async for chunk in run_agent_loop(
                    session=sess,
                    message=message,
                    chat_mode="agent",
                    session_manager=session_manager,
                    config=session_config,
                    webhook_manager=webhook_manager,
                ):
                    result_chunks.append(chunk)
                    yield json.dumps({"content": chunk}) + "\n"

                # Signal completion
                yield json.dumps({"done": True}) + "\n"

            except Exception as e:
                logger.error(f"CLI agent error: {e}")
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(
            event_stream(),
            media_type="application/x-ndjson",
        )

    return router
