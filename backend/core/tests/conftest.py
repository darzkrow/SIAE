import pytest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Usuario administrador para tests"""
    return User.objects.create_superuser(
        username='admin_test',
        email='admin@test.com',
        password='testpass123'
    )


@pytest.fixture
def regular_user(db):
    """Usuario regular para tests"""
    return User.objects.create_user(
        username='user_test',
        email='user@test.com',
        password='testpass123'
    )


@pytest.fixture
def content_types(db):
    """Content types comunes para tests"""
    return {
        'user': ContentType.objects.get_for_model(User),
    }
