import pytest

from auth import get_current_user
from main import app


@pytest.fixture(autouse=True)
def authenticated_user_for_functional_tests(request):
    """Keep endpoint tests focused on behavior, with explicit auth tests exempted."""
    original_overrides = app.dependency_overrides.copy()
    if request.node.get_closest_marker("requires_auth") is None:
        app.dependency_overrides[get_current_user] = lambda: {
            "sub": "pytest-user",
            "role": "authenticated",
        }

    yield

    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
