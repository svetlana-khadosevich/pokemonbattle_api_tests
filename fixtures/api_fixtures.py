import os
from http import HTTPStatus

import allure
import requests
import pytest

from config.api_config import BASE_URL
from data.api_constants import TRAINER_ID_MY
from helpers.api_helpers import ApiSession


@pytest.fixture(scope="session")
def api_session():
    with allure.step("Создаём API-сессию с токеном тренера"):
        with requests.Session() as pokemon_session:
            pokemon_session.headers.update({"trainer_token": os.getenv("POKEMONBATTLE_TOKEN")})
            yield ApiSession(pokemon_session)
            with allure.step("Закрываем API-сессию"):
                pokemon_session.close()

@pytest.fixture()
def prepare_and_clear_battle(api_session: ApiSession):
    response = api_session.get(
        BASE_URL + "/me",
    )
    body = response.json()["data"][0]
    if pokemon_list := body["pokemons_in_pokeballs"]:
        pokemon_id = pokemon_list[0]["id"]
    else:
        if body["pokemons"][0] == 0: # если у тренера нет покемонов, то создаем нового
            response = api_session.post(
                BASE_URL + "/pokemons",
                json={
                    "name": "The Winner",
                    "photo_id": 1
                }
            )
            body = response.json()
            pokemon_id = body["id"]
        else:
            response = api_session.get(   # если есть покемоны, то ищем живых покемонов
                BASE_URL + "/pokemons",
                params={ "trainer_id": TRAINER_ID_MY}
            )
            pokemon_list = response.json()["data"]
            pokemon_id = None
            for pokemon in pokemon_list:
                if pokemon["status"] == 1:
                    pokemon_id = pokemon["id"]
                    break
            if pokemon_id is None:
                response = api_session.post(
                    BASE_URL + "/pokemons",
                    json={
                        "name": "The Winner",
                        "photo_id": 1
                    }
                )
                body = response.json()
                pokemon_id = body["id"]
        response = api_session.post(
            BASE_URL + "/trainers/add_pokeball",
            json={
                "pokemon_id": pokemon_id
            }
        )
        assert response.status_code == HTTPStatus.OK
    yield pokemon_id
    api_session.post(
        BASE_URL + "/pokemons/knockout",
        json={
            "pokemon_id": pokemon_id
        }
    )

