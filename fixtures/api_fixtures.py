import os

import allure
import requests
import pytest

from helpers.api_helpers import ApiSession


@pytest.fixture(scope="session")
def api_session():
    with allure.step("Создаём API-сессию с токеном тренера"):
        with requests.Session() as pokemon_session:
            pokemon_session.headers.update({"trainer_token": os.getenv("POKEMONBATTLE_TOKEN")})
            yield ApiSession(pokemon_session)
            with allure.step("Закрываем API-сессию"):
                pokemon_session.close()
