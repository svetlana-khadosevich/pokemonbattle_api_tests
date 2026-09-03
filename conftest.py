import subprocess

pytest_plugins = ["fixtures.api_fixtures"]


def pytest_addoption(parser):
    parser.addoption(
        "--html-report",
        action="store_true",
        default=False,
        help="Сгенерировать отчёт в формате HTML в директорию allure-report",
    )


def pytest_sessionfinish(session):
    if session.config.getoption("--html-report"):
         subprocess.call(["C:/Users/skhadosevich/allure-2.46.0/allure-2.46.0/bin/allure.bat", "generate", "--clean", "--single-file", "allure-result"])
