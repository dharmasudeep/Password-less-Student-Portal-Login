"""Main site routes."""
from __future__ import annotations

from flask import Blueprint, redirect, url_for
from flask_login import current_user


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("chat.chat"))
    return redirect(url_for("auth.login"))
