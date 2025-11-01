from types import SimpleNamespace


def login(client, email='user@example.com', password='password123'):
    return client.post(
        '/login',
        data={'email': email, 'password': password},
        follow_redirects=True,
    )


def test_chat_api_returns_response(client, user, mocker):
    login(client)
    mocker.patch(
        'app.chat.routes._client',
        return_value=SimpleNamespace(generate=lambda prompt: 'mock reply', stream=lambda prompt: iter([])),
    )
    response = client.post('/api/chat', json={'message': 'hello'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['response'] == 'mock reply'


def test_chat_stream(client, user, mocker):
    login(client)

    def stream_gen(_prompt):
        yield 'mock '
        yield 'stream'

    mocker.patch(
        'app.chat.routes._client',
        return_value=SimpleNamespace(
            generate=lambda prompt: 'mock reply',
            stream=stream_gen,
        ),
    )

    response = client.get('/api/chat/stream?prompt=hello')
    assert response.status_code == 200
    body = b''.join(response.response).decode()
    assert 'mock stream' in body
