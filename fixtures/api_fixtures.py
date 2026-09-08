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
            yield ApiSession(
                pokemon_session,
                base_url=os.getenv("POKEMON_URL")
            )
            with allure.step("Закрываем API-сессию"):
                pokemon_session.close()


@pytest.fixture()
def lavka_api():
    with allure.step("Создаём API-сессию для Лавки"):
        with requests.Session() as lavka_session:
            lavka_session.headers.update({"trainer_token": os.getenv("POKEMONBATTLE_TOKEN")})
            api = ApiSession(
                lavka_session,
                base_url=os.getenv("LAVKA_URL")
            )
            # отменяем премиум на случай, если он был до выполнения теста
            api.post("/cancel_premium")
            yield api
            with allure.step("Закрываем API-сессию Лавки"):
                lavka_session.close()


@pytest.fixture()
def premium_cleanup(lavka_api):
    yield
    with allure.step("Отменяем Premium"):
        response = lavka_api.post("/cancel_premium")
        assert response.status_code == 200
