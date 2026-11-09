from src.config import settings


def test_default_academic_settings_are_available():
    assert settings.neo4j_uri
    assert settings.neo4j_username
    assert settings.app_env == "development"
