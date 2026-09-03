## Pokémon Battle API Tests

Автотесты для API Pokémon Battle

## Стек

- Python 3.15
- pytest
- requests

## Структура
- pokemonbattle_api_tests/

- config/ # BASE_URL

- data/ # константы

- fixtures/ # фикстуры

- helpers/ 

- schemas/ 

- tests/ # Тесты

- .env # Переменные окружения

- conftest.py # фикстуры

- pytest.ini # настройки pytest

- requirements.txt # зависимости


## Тесты

### Получение тренеров (`TestGetTrainer`) — `@pytest.mark.smoke`

- По городу
- По ID
- С сортировкой по уровню

### Изменение покемонов (`TestPatchPokemons`) — `@pytest.mark.regress`

- Изменение имени через PATCH

## Запуск

### Все тесты
python -m pytest

### Только smoke
python -m pytest -m smoke  

### Только regress
python -m pytest -m regress