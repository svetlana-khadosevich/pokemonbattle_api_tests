import allure
import pytest


@allure.title("Тесты на покупку premium")
class TestBuyPremium:
    @allure.title("Позитивный тест покупки premium")
    def test_buy_premium_positive(self, lavka_api, premium_cleanup):
        response = lavka_api.post("/payments",
                                  json={"order_type": "premium",
                                  "details": {
                                        "card_number": "4111 1111 1111 1111",
                                        "secure_code": "56456",
                                        "card_name": "Ivan Ivanov",
                                        "card_cvv": "125",
                                        "card_actual": "12/34",
                                        "days": 50
                                              }
                                        }
                                  )
        assert response.status_code == 200
        me = lavka_api.get("/me")
        assert me.json()["is_premium"] is True

    @pytest.mark.parametrize(
        "field_name, new_value, expected_message",
        [
            ("card_number", "12365458965", "Некорректная длина номера карты"),
            ("secure_code", "562", "Неправильно введен подтверждающий код 3D-secure"),
            ("card_cvv", "300", "Недостаточно средств для оплаты"),
            ("card_actual", "10/24", "Введена некорректная дата окончания срока действия карты, либо срок действия карты истек"),
        ])
    @allure.title("Негативный тест покупки premium")
    def test_buy_premium_negative(self, lavka_api, field_name, new_value, expected_message):
        payload = {"order_type": "premium",
                   "details": {
            "card_number": "4111 1111 1111 1111",
            "secure_code": "56456",
            "card_name": "Ivan Ivanov",
            "card_cvv": "125",
            "card_actual": "12/34",
            "days": 50
        }}
        payload["details"][field_name] = new_value
        response = lavka_api.post("/payments",
                                  json=payload
                                  )
        body = response.json()
        assert response.status_code == 400
        assert body["status"] == "error"
        assert body["message"] == expected_message
