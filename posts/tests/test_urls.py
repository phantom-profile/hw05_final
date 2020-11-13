# posts/tests/tests_url.py

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class StaticURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AndrewGorlov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.unauthorized_client = Client()

    def test_homepage(self):
        response = self.unauthorized_client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_new_post(self):
        current_posts_count = Post.objects.count()
        response = self.authorized_client.post(reverse('new_post'),
                                               {'text': 'test text'},
                                               follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Post.objects.count(), current_posts_count + 1)

    def test_unauthorized_user_newpage(self):
        current_posts_count = Post.objects.count()
        response = self.unauthorized_client.post(reverse('new_post'),
                                                 {'text': 'test text'},
                                                 follow=False)
        login_url = reverse('login')
        newpost_url = reverse('new_post')
        aim_url = login_url + '?next=' + newpost_url
        self.assertRedirects(response,
                             aim_url,
                             status_code=302,
                             target_status_code=200)
        self.assertEqual(Post.objects.count(), current_posts_count)

    def test_profile_url(self):
        response = self.authorized_client.get(reverse('profile',
                                                      args=[self.user]
                                                      ),
                                              username=self.user)
        self.assertEqual(response.status_code, 200)

    def test_404view_404page(self):
        response = self.unauthorized_client.get('unknown-page/')

        self.assertEqual(response.status_code, 404,
                         "не дропается ошибка 404")
        self.assertTemplateUsed(response, 'misc/404.html',
                                "404 страница не появляется")
