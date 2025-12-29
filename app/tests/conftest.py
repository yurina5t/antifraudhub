import sys
import os

sys.path.append(os.path.abspath("."))

import pytest
from fastapi.testclient import TestClient
from app.api import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)
