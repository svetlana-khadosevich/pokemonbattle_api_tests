import os

import requests
import pytest


@pytest.fixture(scope="session")
def api_session():
    with requests.Session() as pokemon_session:
        pokemon_session.headers.update({"trainer_token": os.getenv("POKEMONBATTLE_TOKEN")})
        yield pokemon_session
