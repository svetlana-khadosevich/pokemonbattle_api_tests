from http import HTTPStatus

from requests import Session
from jsonschema import validate
from deepdiff import DeepDiff

import pytest

from data.api_constants import TRAINER_ID
from data.api_constants import TRAINER_ID_MY
from config.api_config import BASE_URL
from helpers.file_helpers import load_yaml


# Задание 2
class TestGetTrainer:
    '''Тесты на метод GET/trainers'''
    # получение тренеров по городу
    @pytest.mark.smoke
    def test__get_trainer_by_city__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"city": "Москва"}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        for trainer in body["data"]:
            assert trainer["city"] == "Москва"

    # получение тренеров по ID
    @pytest.mark.smoke
    def test__get_trainer_by_id__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"trainer_id": TRAINER_ID}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["data"][0]["id"] == TRAINER_ID

    # получение тренеров по городу с сортировкой по убыванию уровня
    @pytest.mark.smoke
    @pytest.mark.skip
    def test__get_trainer_by_city_desc_level__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"city": "Москва", "sort": "desc_level"}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        trainers = body.get('data', [])
        for i in range(len(trainers) - 1):
            current_level = int(trainers[i].get('level', 0))
            next_level = int(trainers[i + 1].get('level', 0))
            assert current_level >= next_level


# Задание 3
class TestPutPokemons:
    '''Тесты на метод PUT/pokemons'''
    # функция, которая меняет имя покемона через PATCH
    @pytest.mark.regress
    def test_change_pokemons_name(self, api_session: Session) -> None:
        # функция, которая нокаутирует всех покемонов тренера через POST
        def knockout_all_trainers_pokemons(api_session: Session) -> None:
            response = api_session.get(
                BASE_URL + "/pokemons",
                params={"trainer_id": TRAINER_ID_MY},
            )
            body = response.json()
            for pokemon_id in [x['id'] for x in body["data"] if x["status"] == 1]:
                response = api_session.post(
                    BASE_URL + "/pokemons/knockout",
                    json={"pokemon_id": pokemon_id}
                )
                assert response.status_code == HTTPStatus.OK

            response = api_session.get(
                BASE_URL + '/pokemons',
                params={"trainer_id": TRAINER_ID_MY}
            )
            body = response.json()
            for pokemon in body["data"]:
                assert pokemon["status"] == 0

        # функция, которая создает нового покемона через POST
        def create_pokemon(api_session: Session) -> str:
            response = api_session.post(
                BASE_URL + '/pokemons',
                json={
                    "name": "Tayler",
                    "photo_id": 1
                }
            )
            assert response.status_code == HTTPStatus.CREATED
            pokemon_id = response.json()["id"]
            return pokemon_id

        # код - тело самого теста
        knockout_all_trainers_pokemons(api_session)
        pokemon_id = create_pokemon(api_session)

        response = api_session.patch(
            BASE_URL + '/pokemons',
            json={"pokemon_id": pokemon_id,
                  "name": "John",
                  "photo_id": 1
                  }
        )
        body = response.json()
        # проверки, что информация о покемоне изменилась
        assert response.status_code == HTTPStatus.OK
        assert body["message"] == "Информация о покемоне обновлена"

        # получение информации о покемоне через ручку GET
        response = api_session.get(
            BASE_URL + '/pokemons',
            params={"pokemon_id": pokemon_id}
        )
        body = response.json()
        # проверки, что у покемона действительно новое имя
        assert response.status_code == HTTPStatus.OK
        assert body["data"][0]["name"] == "John"


# Задание 1. JSON схема

class TestGetBattle:
    '''Проверка схемы ответа метода GET/battle'''
    def test__get_battle(self, api_session: Session) -> None:
        response = api_session.get(
             BASE_URL + '/battle'
                                  )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        template = load_yaml("get_battle.yml")
        validate(body, template)


# Задание 2. DeepDiff
class TestGetAchievements:
    '''Проверка схемы ответа метода GET/achievements'''
    def test__get_achievements(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/achievements'
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        template = load_yaml("get_achievements.yml")
        validate(body, template)

        template1 = {
            "data": [
                {
                    "slug": "beginning",
                    "is_reached": False
                },
                {
                    "slug": "out_of_battles",
                    "is_reached": False
                },
                {
                    "slug": "self_knockout",
                    "is_reached": False
                },
                {
                    "slug": "max_level"
                },
                {
                    "slug": "one_vs_seven",
                    "is_reached": False
                },
                {
                    "slug": "five_battles",
                    "is_reached": False
                },
                {
                    "slug": "three_defends",
                    "is_reached": False
                }
            ]
        }
        compare = DeepDiff(
            template1, body,
            exclude_regex_paths=[
                r"root\['data'\]\[\d+\]\['is_reached'\]"

            ]
        )
        assert not compare, compare

# Задание 3. Soft Asserts
    def test__get_achievements__negative(self, api_session: Session, check) -> None:
        response = api_session.get(
            BASE_URL + '/achievements',
            params={"trainer_id": TRAINER_ID_MY,
                    "is_reached": "522"
                    }
                                   )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        body = response.json()
        with check:
            assert body["status"] == "error"
        with check:
            assert body["message"] != ""
