import pytest


def test_root_redirects_to_index(client):
    """Test that root path redirects to /static/index.html"""
    # Use allow_redirects=False to capture the redirect response
    response = client.get("/", follow_redirects=False)
    
    # Should be a redirect status code
    assert response.status_code in [301, 302, 303, 307, 308]
    
    # Should redirect to /static/index.html
    assert response.headers["location"] == "/static/index.html"


def test_root_final_destination(client):
    """Test that root path eventually serves index.html"""
    # Follow redirects to get the final response
    response = client.get("/", follow_redirects=True)
    
    assert response.status_code == 200
    # Should contain HTML content
    assert "html" in response.text.lower()
