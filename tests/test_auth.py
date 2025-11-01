from app.models import User


def test_register_and_login(client, app):
    response = client.post(
        '/register',
        data={
            'email': 'new@example.com',
            'password': 'password123',
            'confirm': 'password123',
        },
        follow_redirects=True,
    )
    assert b'Welcome' in response.data

    with app.app_context():
        assert User.query.filter_by(email='new@example.com').one()

    client.post('/logout', follow_redirects=True)

    response = client.post(
        '/login',
        data={
            'email': 'new@example.com',
            'password': 'password123',
        },
        follow_redirects=True,
    )
    assert b'Assistant' in response.data


def test_protected_routes_require_login(client):
    response = client.get('/chat')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
