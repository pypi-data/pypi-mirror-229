import re

from django.contrib.auth import get_user_model
from django.test import override_settings
from pytest_data import use_data

from cms_qe_auth.tests.utils import reset_urls


@override_settings(CMS_QE_AUTH_ENABLED=True)
@use_data(user_data={'username': 'testuser', 'password': 'testpass'})
def test_login(client, user):
    reset_urls()
    res = client.post('/en/auth/login/', {'username': 'testuser', 'password': 'testpass'})
    assert res.status_code == 302


@override_settings(CMS_QE_AUTH_ENABLED=True)
def test_register(mailoutbox, client):
    assert len(mailoutbox) == 0
    assert not get_user_model().objects.filter(username='testuser')

    reset_urls()
    user = _register_user(client)

    assert user.email == 'testuser@example.com'
    assert len(mailoutbox) == 1
    activation_mail = mailoutbox[0]
    assert 'activate' in activation_mail.body
    assert 'http' in activation_mail.body


@override_settings(AUTHENTICATION_BACKENDS=[
    'django.contrib.auth.backends.ModelBackend',
    'cms_qe_auth.tests.utils.TestAuthBackend',
], CMS_QE_AUTH_ENABLED=True)
def test_activation_multiple_authentication_backends(client, mailoutbox):
    _test_activation(client, mailoutbox)


@override_settings(CMS_QE_AUTH_ENABLED=True)
def test_activation(client, mailoutbox):
    _test_activation(client, mailoutbox)


def _test_activation(client, mailoutbox):
    reset_urls()
    user = get_user_model()(username='testuser', email='testuser@example.com', is_active=False)
    user.save(base_url="http://example.com")

    # Get activation link from email
    activation_mail = mailoutbox[0]
    activate_url_pattern = r'(?P<url>https?://[^\s]+/activate/[^\s]+)'
    url = re.search(activate_url_pattern, activation_mail.body).group('url')

    response = client.get(url)
    user.refresh_from_db()

    assert user.is_active
    # Test automatic login
    assert response.context['user'].is_authenticated


def _register_user(client):
    res = client.post('/en/auth/register/', {
        'username': 'testuser',
        'password1': '179ad45c6ce2cb97cf1029e212046e81',
        'password2': '179ad45c6ce2cb97cf1029e212046e81',
        'email': 'testuser@example.com',
    })
    assert res.status_code == 302
    return get_user_model().objects.get(username='testuser')
