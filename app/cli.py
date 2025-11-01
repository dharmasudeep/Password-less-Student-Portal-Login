"""Custom Flask CLI commands."""
from __future__ import annotations

import click
from flask.cli import with_appcontext

from .extensions import db
from .models import ChatMessage, User


@click.command("create-admin")
@click.argument("email")
@with_appcontext
def create_admin(email: str) -> None:
    """Promote a user to admin or create them if missing."""
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
        user = User(email=email.lower())
        user.set_password(password)
        db.session.add(user)
    user.is_admin = True
    db.session.commit()
    click.echo(f"{email} is now an admin")


@click.command("list-users")
@with_appcontext
def list_users() -> None:
    """List registered users."""
    users = User.query.order_by(User.created_at.asc()).all()
    for user in users:
        click.echo(f"{user.id}: {user.email} admin={user.is_admin} created={user.created_at}")


@click.command("clear-messages")
@with_appcontext
def clear_messages() -> None:
    """Delete all chat messages."""
    deleted = ChatMessage.query.delete()
    db.session.commit()
    click.echo(f"Deleted {deleted} messages")
