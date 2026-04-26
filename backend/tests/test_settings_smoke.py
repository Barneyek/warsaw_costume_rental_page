import pytest
from django.conf import settings


# ── Settings integrity ────────────────────────────────────────────────────────

def test_installed_apps_contains_all_local_apps():
    expected = {'src.core', 'src.catalogue', 'src.blog', 'src.pages', 'src.inquiry'}
    assert expected.issubset(set(settings.INSTALLED_APPS))


def test_modeltranslation_before_admin():
    apps = list(settings.INSTALLED_APPS)
    assert 'modeltranslation' in apps, "modeltranslation must be in INSTALLED_APPS"
    assert apps.index('modeltranslation') < apps.index('django.contrib.admin'), (
        "modeltranslation must appear before django.contrib.admin"
    )


def test_drf_spectacular_in_installed_apps():
    assert 'drf_spectacular' in settings.INSTALLED_APPS


def test_cors_middleware_is_first():
    assert settings.MIDDLEWARE[0] == 'corsheaders.middleware.CorsMiddleware', (
        f"CorsMiddleware must be first, got: {settings.MIDDLEWARE[0]}"
    )


def test_secret_key_is_set_and_not_empty():
    assert settings.SECRET_KEY, "SECRET_KEY must not be empty"
    assert len(settings.SECRET_KEY) >= 20, "SECRET_KEY suspiciously short"


def test_language_code_matches_languages():
    codes = [code for code, _ in settings.LANGUAGES]
    assert settings.LANGUAGE_CODE in codes, (
        f"LANGUAGE_CODE '{settings.LANGUAGE_CODE}' not found in LANGUAGES codes: {codes}"
    )


def test_modeltranslation_default_language():
    assert settings.MODELTRANSLATION_DEFAULT_LANGUAGE == 'pl'


def test_modeltranslation_fallback_languages():
    assert 'pl' in settings.MODELTRANSLATION_FALLBACK_LANGUAGES


def test_spectacular_component_split_request():
    assert settings.SPECTACULAR_SETTINGS.get('COMPONENT_SPLIT_REQUEST') is True, (
        "COMPONENT_SPLIT_REQUEST must be True for orval compatibility"
    )


def test_spectacular_serve_include_schema_false():
    assert settings.SPECTACULAR_SETTINGS.get('SERVE_INCLUDE_SCHEMA') is False


def test_media_root_configured():
    assert settings.MEDIA_ROOT is not None
    assert 'media' in str(settings.MEDIA_ROOT).lower()


def test_use_i18n_and_tz():
    assert settings.USE_I18N is True
    assert settings.USE_TZ is True
    assert settings.TIME_ZONE == 'Europe/Warsaw'


# ── OpenAPI endpoints ─────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_api_schema_returns_200(client):
    """
    /api/schema/ must return 200.
    This endpoint is the contract for orval in issue #14.
    A 404 means drf_spectacular URLs are missing from urls.py.
    A 500 means a serializer or view has a misconfiguration.
    """
    response = client.get('/api/schema/')
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        "Check that 'drf_spectacular' is in INSTALLED_APPS and "
        "SpectacularAPIView is wired in web_app/urls.py."
    )


@pytest.mark.django_db
def test_api_schema_content_type_is_openapi(client):
    response = client.get('/api/schema/')
    content_type = response.get('Content-Type', '')
    assert 'openapi' in content_type or 'yaml' in content_type or 'json' in content_type, (
        f"Unexpected Content-Type: {content_type}"
    )


@pytest.mark.django_db
def test_api_docs_returns_200(client):
    """
    /api/docs/ must return 200 HTML.
    A 404 means SpectacularSwaggerView is not wired in urls.py.
    """
    response = client.get('/api/docs/')
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. "
        "Check SpectacularSwaggerView in web_app/urls.py."
    )
    assert b'swagger' in response.content.lower() or b'openapi' in response.content.lower()


@pytest.mark.django_db
def test_database_connection():
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        assert cursor.fetchone() == (1,)
