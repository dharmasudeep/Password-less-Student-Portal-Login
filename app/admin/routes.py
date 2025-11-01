"""Admin routes."""
from __future__ import annotations

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from ..models import User


bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin() -> None:
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@bp.route("/users")
@login_required
def users():
    _require_admin()
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin.html", users=users)
