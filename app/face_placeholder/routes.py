"""Placeholder blueprint for future face recognition features."""
from __future__ import annotations

from flask import Blueprint, jsonify


bp = Blueprint("face", __name__)


@bp.get("/status")
def face_status():
    """Temporary endpoint until face recognition is implemented."""
    return jsonify({"implemented": False, "todo": "Face enrollment and verification endpoints"})


# TODO: Implement face enrollment endpoint
# @bp.post("/enroll")
# def enroll_face():
#     pass

# TODO: Implement face verification endpoint
# @bp.post("/verify")
# def verify_face():
#     pass
