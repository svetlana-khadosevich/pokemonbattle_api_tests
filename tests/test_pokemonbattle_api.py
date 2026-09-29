from http import HTTPStatus

import allure
from requests import Session
from jsonschema import validate
from deepdiff import DeepDiff

import pytest

from data.api_constants import TRAINER_ID
from data.api_constants import TRAINER_ID_MY
from config.api_config import BASE_URL
from helpers.api_helpers import ApiSession
from helpers.file_helpers import load_yaml


# Задание 2
@allure.suite("Тесты на метод GET/trainers")
class TestGetTrainer:
    @allure.title("Получение тренера по городу 'city:Москва'")
    @pytest.mark.smoke
    @pytest.mark.api
    def test__get_trainer_by_city__positive(self, api_session: Session) -> None:
        with allure.step("Получаем список тренеров по городу"):
            response = api_session.get(
               '/trainers',
                params={"city": "Москва"}
            )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        with allure.step("Проверяем телло ответа"):
            body = response.json()
        with allure.step("Проверяем, что во всех объектах, город соответствует переданному при отправке запроса"):
            for trainer in body["data"]:
                assert trainer["city"] == "Москва"

    @allure.title("Получение тренера по ID")
    @pytest.mark.smoke
    @pytest.mark.api
    def test__get_trainer_by_id__positive(self, api_session: Session) -> None:
        response = api_session.get(
            '/trainers',
            params={"trainer_id": TRAINER_ID}
        )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        with allure.step("Проверяем телло ответа"):
            body = response.json()
        assert body["data"][0]["id"] == TRAINER_ID

    @allure.title("Получение тренеров по городу с сортировкой по убыванию уровня")
    @pytest.mark.smoke
    def test__get_trainer_by_city_desc_level__positive(self, api_session: Session) -> None:
        response = api_session.get(
            '/trainers',
            params={"city": "Москва", "sort": "desc_level"}
        )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        with allure.step("Проверяем телло ответа"):
            body = response.json()
        with allure.step("Проверяем сортировку"):
            trainers = body.get('data', [])
            for i in range(len(trainers) - 1):
                current_level = int(trainers[i].get('level', 0))
                next_level = int(trainers[i + 1].get('level', 0))
                assert current_level >= next_level


# Задание 3
@allure.suite("Тесты на метод PATCH/pokemons")
class TestPatchPokemons:
    @allure.title("Изменение имени покемона PATCH/pokemons")
    @pytest.mark.regress
    def test_change_pokemons_name(self, api_session: Session) -> None:
        def knockout_all_trainers_pokemons(api_session: Session) -> None:
            response = api_session.get(
                "/pokemons",
                params={"trainer_id": TRAINER_ID_MY},
            )
            body = response.json()
            for pokemon_id in [x['id'] for x in body["data"] if x["status"] == 1]:
                response = api_session.post(
                    "/pokemons/knockout",
                    json={"pokemon_id": pokemon_id}
                )
                assert response.status_code == HTTPStatus.OK

            response = api_session.get(
                '/pokemons',
                params={"trainer_id": TRAINER_ID_MY}
            )
            body = response.json()
            for pokemon in body["data"]:
                assert pokemon["status"] == 0

        @allure.step("Создаем нового покемона через POST")
        def create_pokemon(api_session: Session) -> str:
            response = api_session.post(
                '/pokemons',
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
            '/pokemons',
            json={"pokemon_id": pokemon_id,
                  "name": "John",
                  "photo_id": 1
                  }
        )
        body = response.json()
        with allure.step("Проверка, что имя покемона изменилось"):
            assert response.status_code == HTTPStatus.OK
            assert body["message"] == "Информация о покемоне обновлена"
        response = api_session.get(
            '/pokemons',
            params={"pokemon_id": pokemon_id}
        )
        body = response.json()
        assert response.status_code == HTTPStatus.OK
        assert body["data"][0]["name"] == "John"


# Задание 1. JSON схема
@allure.suite("Тесты на метод GET/battle")
class TestGetBattle:
    @allure.title("Проверка схемы ответа метода")
    @pytest.mark.api
    def test__get_battle(self, api_session: Session) -> None:
        response = api_session.get(
             '/battle'
                                  )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.OK
        body = response.json()
        template = load_yaml("get_battle.yml")
        with allure.step("Проверяем тело ответа на соответствие схеме"):
            validate(body, template)


# Задание 2. DeepDiff
@allure.suite("Тесты на метод GET/achievements")
class TestGetAchievements:
    @allure.title("Проверка схемы ответа метода")
    def test__get_achievements(self, api_session: Session) -> None:
        response = api_session.get(
            '/achievements'
        )
        with allure.step("Проверяем код ответа"):
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
        with allure.step("С помощью DeepDiff проверяем, что тело ответа соответствует шаблону, игнорируя 'is_reached'"):
            assert not compare, compare

# Задание 3. Soft Asserts
    @allure.title("Негативный тест 422 UnprocessableEntity")
    def test__get_achievements__negative(self, api_session: Session, check) -> None:
        response = api_session.get(
            '/achievements',
            params={"trainer_id": TRAINER_ID_MY,
                    "is_reached": "522"
                    }
                                   )
        with allure.step("Проверяем код ответа"):
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        body = response.json()
        with check:
            assert body["status"] == "error"
        with check:
            assert body["message"] != ""


@allure.suite("Тесты прохождения битвы покемонов")
class TestPokemonBattle:
    @allure.title("Битва покемонов: успешное прохождение")
    def test_run_battle_successfully(self, api_session: ApiSession, prepare_and_clear_battle: str):
        with allure.step("Находим нашему покемону соперника"):
            ready_for_battle_response = api_session.get(
                BASE_URL + "/pokemons",
                params={"in_pokeball": 1}
            )
            assert ready_for_battle_response.status_code == HTTPStatus.OK
            body = ready_for_battle_response.json()
            suitable_pokemons = [x for x in body["data"] if x["trainer_id"] != TRAINER_ID_MY]
            enemy_pokemon_id = suitable_pokemons[0]["id"]
        with allure.step("Проводим битву"):
            battle_response = api_session.post(
                BASE_URL + "/battle",
                json={
                  "attacking_pokemon": prepare_and_clear_battle,
                  "defending_pokemon": enemy_pokemon_id
                }
            )
            assert battle_response.status_code == HTTPStatus.OK
            body = battle_response.json()
            assert body["message"] == "Битва проведена"
            if body["result"] == "Твой покемон проиграл":
                with allure.step("Проверяем статус покемона после проигрыша"):
                    response = api_session.get(
                        BASE_URL + "/pokemons/" + str(prepare_and_clear_battle)
                    )
                    body = response.json()
                    assert body["in_pokeball"] == 0
                    assert body["status"] == 0
            else:
                with allure.step("Проверяем статус покемона после выигрыша"):
                    response = api_session.get(
                        BASE_URL + "/pokemons/" + str(prepare_and_clear_battle)
                    )
                    body = response.json()
                    assert body["status"] == 1


