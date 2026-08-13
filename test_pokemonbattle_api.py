from http import HTTPStatus
from requests import Session

import requests
import pytest

BASE_URL = "https://api.pokemonbattle.ru/v2"
AUTH_HEADER={"trainer_token": "92a0aef22db567f6a74669289c577f6a"}

@pytest.fixture(scope="session")
def api_session():
    with requests.Session() as pokemon_session:
        pokemon_session.headers.update(AUTH_HEADER)
        yield pokemon_session

#Задание 2
class TestGetTrainer:
    # получение тренеров по городу
    def test__get_trainer_by_city__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"city":"Москва"}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        for trainer in body["data"]:
            assert trainer["city"]=="Москва"

    # получение тренеров по ID
    def test__get_trainer_by_id__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"trainer_id":"66624"}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert body["data"][0]["id"]=="66624"

    # получение тренеров по городу с сортировкой по убыванию уровня
    def test__get_trainer_by_city_desc_level__positive(self, api_session: Session) -> None:
        response = api_session.get(
            BASE_URL + '/trainers',
            params={"city":"Москва", "sort":"desc_level"}
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        trainers = body.get('data', [])
        for i in range(len(trainers) - 1):
            current_level = int(trainers[i].get('level', 0))
            next_level = int(trainers[i + 1].get('level', 0))
            assert current_level >= next_level

#Задание 3
class TestPatchPokemons:
    # функция, которая меняет имя покемона через PATCH
    def test_change_pokemons_name(self, api_session: Session) -> None:
        # функция, которая нокаутирует всех покемонов тренера через POST
        def knockout_all_trainers_pokemons(api_session: Session) -> None:
            response = api_session.get(
                BASE_URL + "/pokemons",
                params={"trainer_id": 66618},
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
                params={"trainer_id": 66618}
            )
            body = response.json()
            for pokemon in body["data"]:
                assert pokemon["status"] == 0

        # функция, которая создает нового покемона через POST
        def create_pokemon(api_session:Session) -> str:
            response = api_session.post(
                BASE_URL + '/pokemons',
                json = {
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

        #получение информации о покемоне через ручку GET
        response = api_session.get(
            BASE_URL + '/pokemons',
            params={"pokemon_id": pokemon_id}
        )
        body = response.json()
        # проверки, что у покемона действительно новое имя
        assert response.status_code == HTTPStatus.OK
        assert body["data"][0]["name"] == "John"



