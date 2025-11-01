"""Chat routes and API endpoints."""
from __future__ import annotations

from typing import Generator

from flask import Blueprint, Response, current_app, jsonify, render_template, request
from flask_login import current_user, login_required

from ..extensions import db, limiter
from ..models import ChatMessage
from .llm_client import LlmClient


bp = Blueprint("chat", __name__)


def _client() -> LlmClient:
    return LlmClient(
        host=current_app.config["OLLAMA_HOST"],
        model=current_app.config["OLLAMA_MODEL"],
    )


def _recent_messages(limit: int = 10) -> list[ChatMessage]:
    return (
        ChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]
    )


def _build_prompt(user_message: str) -> str:
    history = _recent_messages()
    lines = ["System: You are a helpful assistant."]
    for msg in history:
        lines.append(f"{msg.role.capitalize()}: {msg.content}")
    lines.append(f"User: {user_message}")
    lines.append("Assistant:")
    return "\n".join(lines)


@bp.route("/chat")
@login_required
def chat():
    messages = (
        ChatMessage.query.filter_by(user_id=current_user.id)
        .order_by(ChatMessage.created_at.asc())
        .limit(50)
        .all()
    )
    return render_template("chat.html", messages=messages)


@bp.route("/api/chat", methods=["POST"])
@login_required
@limiter.limit(lambda: current_app.config["RATE_LIMIT"])
def chat_api():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Message is required"}), 400

    prompt = _build_prompt(message)

    user_msg = ChatMessage(user_id=current_user.id, role="user", content=message)
    db.session.add(user_msg)

    try:
        response_text = _client().generate(prompt)
    except Exception as exc:  # pragma: no cover - network errors
        db.session.rollback()
        current_app.logger.exception("Ollama request failed")
        return jsonify({"error": "LLM service unavailable", "details": str(exc)}), 503

    assistant_msg = ChatMessage(
        user_id=current_user.id, role="assistant", content=response_text
    )
    db.session.add(assistant_msg)
    db.session.commit()

    return jsonify({"response": response_text})


@bp.route("/api/chat/stream")
@login_required
@limiter.limit(lambda: current_app.config["RATE_LIMIT"])
def chat_stream() -> Response:
    prompt_text = (request.args.get("prompt") or "").strip()
    if not prompt_text:
        return jsonify({"error": "Prompt is required"}), 400

    prompt = _build_prompt(prompt_text)
    user_msg = ChatMessage(user_id=current_user.id, role="user", content=prompt_text)
    db.session.add(user_msg)
    db.session.commit()

    def event_stream() -> Generator[str, None, None]:
        collected: list[str] = []
        try:
            for chunk in _client().stream(prompt):
                if chunk:
                    collected.append(chunk)
                    yield f"data: {chunk}\n\n"
        except Exception as exc:  # pragma: no cover
            current_app.logger.exception("Streaming failed")
            db.session.rollback()
            yield f"event: error\ndata: {str(exc)}\n\n"
            return

        full_text = "".join(collected)
        assistant_msg = ChatMessage(
            user_id=current_user.id, role="assistant", content=full_text
        )
        db.session.add(assistant_msg)
        db.session.commit()
        yield "event: done\ndata: end\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "text/event-stream",
        "X-Accel-Buffering": "no",
    }
    return Response(event_stream(), headers=headers)


@bp.route("/api/chat/clear", methods=["POST"])
@login_required
def clear_chat():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"cleared": True})
