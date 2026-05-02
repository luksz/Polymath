from polymath_core.config import Settings


def test_default_environment():
    s = Settings()
    assert s.environment == "development"


def test_is_development():
    s = Settings()
    assert s.is_development is True
    assert s.is_production is False


def test_is_production():
    s = Settings(environment="production")
    assert s.is_production is True
    assert s.is_development is False


def test_default_database_url_has_asyncpg():
    s = Settings()
    assert "asyncpg" in s.database_url


def test_service_name_default():
    s = Settings()
    assert s.service_name == "polymath-service"
