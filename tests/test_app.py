# tests/test_app.py
# Basic unit tests for models.py

import os
import models

def test_database_created():
    """Check if database file exists after import."""
    assert os.path.exists(models.DB)

def test_create_user_and_login():
    """Create a new user and verify password check works."""
    email = "pytestuser@example.com"
    password = "pytest123"
    # Ensure DB initialized
    models.init_db()
    # Create user
    models.create_user(email, password)
    # Verify login works
    assert models.verify_user(email, password) == True

def test_create_and_fetch_task():
    """Create a task and confirm it is retrievable."""
    user = models.get_user_by_email("pytestuser@example.com")
    assert user is not None
    models.create_task(user["id"], "TestingTask", "desc", "2025-12-31", "High")
    tasks = models.get_tasks_for_user(user["id"])
    titles = [t["title"] for t in tasks]
    assert "TestingTask" in titles
