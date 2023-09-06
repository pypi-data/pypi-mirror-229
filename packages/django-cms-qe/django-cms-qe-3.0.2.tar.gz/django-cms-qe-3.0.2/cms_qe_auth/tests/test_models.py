import re

from django.test import override_settings
from django.urls.converters import SlugConverter
from pytest_data import use_data

from cms_qe_auth.models import User
from cms_qe_auth.tests.utils import reset_urls
from cms_qe_auth.utils import pk_to_uidb64


def test_set_username_by_email():
    user = User(email='user@example.com')
    assert not user.username
    user.save()
    assert user.username == user.email


@use_data(user_data={'username': 'user@example.com', 'email': 'user@example.com'})
def test_set_username_by_changing_email(user):
    assert user.username == 'user@example.com'
    user.email = 'another@example.com'
    assert user.username == 'user@example.com'
    user.save()
    assert user.username == 'another@example.com'


@use_data(user_data={'email': 'user@example.com'})
def test_unset_is_active_by_changing_email(user):
    assert user.is_active
    user.email = 'another@example.com'
    assert user.is_active
    user.save()
    assert not user.is_active


def test_simple_token_generation_and_checking(user):
    token = user._generate_activation_token()
    assert user._check_activation_token(token)


@use_data(user_data={'is_active': False})
def test_simple_token_generation_and_activate_is_active(user):
    assert not user.is_active
    token = user._generate_activation_token()
    user.activate(token)
    assert user.is_active


@use_data(user_data={'is_active': False})
def test_simple_token_generation_and_activate_invalid(user):
    user._generate_activation_token()
    assert not user.activate("123456789ABZ-987654321abcdefg")
    assert not user.is_active


@override_settings(CMS_QE_AUTH_ENABLED=True)
def test_activation_email_sending(mailoutbox):
    reset_urls()
    user = User(username='testuser', email='testuser@example.com', is_active=False)
    user.save(base_url="http://example.com")
    assert len(mailoutbox) == 1
    email = mailoutbox[0]
    assert user.email == email.to[0]
    assert 'activate' in email.subject.lower()
    token_re = f'(?P<token>{SlugConverter.regex})'
    url_re = fr'//example.com/en/auth/activate/{pk_to_uidb64(user.pk)}/{token_re}'
    match = re.findall(url_re, email.body)
    assert match
    assert user._check_activation_token(match[0])
