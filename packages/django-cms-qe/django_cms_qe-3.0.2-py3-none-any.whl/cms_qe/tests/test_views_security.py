from constance import config
from django.test import TestCase
from django.urls import reverse


class SecurityTxtViewTest(TestCase):

    def test_not_content(self):
        config.SECURITY_TXT_CONTENT = None
        response = self.client.get(reverse('security-txt'))
        self.assertRedirects(response, "/en/.well-known/security.txt/",
                             status_code=302, target_status_code=404)

    def test_content(self):
        config.SECURITY_TXT_CONTENT = 'Contact: https://abuse.foo'
        response = self.client.get(reverse('security-txt'))
        self.assertContains(response, b'Contact: https://abuse.foo')
        self.assertEqual(response['Content-Type'], 'text/plain')
