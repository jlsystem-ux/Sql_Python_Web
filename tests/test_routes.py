def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"SQL for Testers" in response.data

def test_lesson_page(client):
    """Test that a lesson page loads successfully."""
    response = client.get('/lesson/1')
    assert response.status_code == 200
    assert b"Introducci" in response.data

def test_non_existent_lesson(client):
    """Test that a non-existent lesson returns 404."""
    response = client.get('/lesson/999')
    assert response.status_code == 404
    assert b"no existe" in response.data

def test_login_page(client):
    """Test that the login page loads."""
    response = client.get('/loginForm')
    assert response.status_code == 200
    assert b"Iniciar" in response.data
