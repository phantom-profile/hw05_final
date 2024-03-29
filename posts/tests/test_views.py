# posts/tests/tests_views.py

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Post, Group

User = get_user_model()


class ViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='AndrewGorlov')
        cls.second_user = User.objects.create_user(username='GorloAndreew')
        cls.unauthorized_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(title='test_group', slug='test-group')

    def test_new_post_on_pages(self):
        new_post = Post.objects.create(author=self.user,
                                       group=self.group,
                                       text='test text 2')
        tested_urls = [
            reverse('index'),
            reverse('profile', args=[self.user]),
            reverse('post_view', args=[self.user, new_post.id]),
            reverse('group_posts', args=[new_post.group.slug]),
        ]

        for url in tested_urls:
            response = self.authorized_client.get(url)
            if 'page' in response.context:
                page1 = response.context['page']
                self.assertEqual(page1[0], new_post,
                                 f"Пост не появляется на {url}")
            else:
                self.assertEqual(response.context['post'], new_post,
                                 f"Измененный пост не появляется на {url}")

    def test_edited_post_on_pages(self):
        new_post = Post.objects.create(author=self.user,
                                       group=self.group,
                                       text='test text 3')
        edit_text = 'new_text'
        response = self.authorized_client.post(
            reverse('post_edit', args=[self.user, new_post.id]),
            {'text': edit_text, 'group': self.group.id},
            follow=True)

        self.assertEqual(response.status_code, 200,
                         "Страница редактирования поста не работает")

        edited_post = Post.objects.first()
        tested_urls = [
            reverse('index'),
            reverse('profile', args=[self.user]),
            reverse('post_view', args=[self.user, new_post.id]),
            reverse('group_posts', args=[new_post.group.slug]),
        ]

        self.assertEqual(edited_post.text, edit_text, "Пост не отредактирован")

        for url in tested_urls:
            response = self.authorized_client.get(url)
            if 'page' in response.context:
                page1 = response.context['page']
                self.assertEqual(page1[0].text, edit_text,
                                 f"Измененный пост не появляется на {url}")
            else:
                self.assertEqual(response.context['post'].text, edit_text,
                                 f"Измененный пост не появляется на {url}")

    def test_is_image_on_page(self):
        image = SimpleUploadedFile('image.jpg',
                                   b'/9j/4AAQSkZJRgABAQAAYABgAAD/4QCMRXhpZ',
                                   content_type='image/jpg'
                                   )

        new_post = Post.objects.create(author=self.user,
                                       group=self.group,
                                       text='test text 3',
                                       image=image)

        cache.clear()
        tested_urls = [
            reverse('index'),
            reverse('profile', args=[self.user]),
            reverse('post_view', args=[self.user, new_post.id]),
            reverse('group_posts', args=[new_post.group.slug]),
        ]
        for url in tested_urls:
            response = self.authorized_client.get(url)
            self.assertTrue('<img class="card-img"' in str(response.content),
                            f'картинки нет на странице {url}')

    def test_defence_from_nonimage_file(self):
        non_image = SimpleUploadedFile('file.txt', b'i am not an image')
        new_post = self.authorized_client.post(
                reverse('new_post'), {'text': 'post with image',
                                      'group': self.group.id,
                                      'image': non_image},
                follow=True)

        self.assertFormError(new_post, 'form', 'image',
                             'Загрузите правильное изображение. '
                             'Файл, который вы загрузили, поврежден '
                             'или не является изображением.')

    def test_cache_index(self):
        testing_post = self.authorized_client.post(
            reverse('new_post'),
            {'text': 'cache checking', 'group': self.group.id, },
            follow=True)
        index = self.authorized_client.get(reverse('index'))
        self.assertFalse('cache checking' in str(index.content),
                         "Страница не закеширована")

    def test_auth_user_follow(self):
        follow = self.authorized_client.post(
            reverse('profile_follow', args=[self.second_user]),
            follow=True)
        self.assertEqual(follow.status_code, 200,
                         "Ссылка 'profile_follow' не работает")
        self.assertTrue(self.user.follower.all(),
                        "У пользователя не появилась подписка")
        self.assertTrue(self.second_user.following.all(),
                        "У второго пользователя не появился подписчик")

    def test_auth_user_unfollow(self):
        unfollow = self.authorized_client.post(
            reverse('profile_unfollow', args=[self.second_user]),
            follow=True)
        self.assertEqual(unfollow.status_code, 200,
                         "Ссылка 'profile_unfollow' не работает")
        self.assertFalse(self.user.follower.all(),
                         "У пользователя не исчезла подписка")
        self.assertFalse(self.second_user.following.all(),
                         "У второго пользователя не исчез подписчик")

    def test_follow_index_followed(self):
        follow = self.authorized_client.post(
            reverse('profile_follow', args=[self.second_user]),
            follow=True)
        new_post = Post.objects.create(author=self.second_user,
                                       group=self.group,
                                       text='post for follower')
        follow_index = self.authorized_client.get(reverse('follow_index'))
        self.assertIn(new_post, follow_index.context['page'],
                      "Пост автора не отображается у подписчика")

    def test_follow_index_unfollowed(self):
        unfollow = self.authorized_client.post(
            reverse('profile_unfollow', args=[self.second_user]),
            follow=True)
        new_post = Post.objects.create(author=self.second_user,
                                       group=self.group,
                                       text='post for follower')
        follow_index = self.authorized_client.get(reverse('follow_index'))
        self.assertNotIn(new_post, follow_index.context['page'],
                         "Пост автора отображается не у подписчика")

    def test_defence_from_unauth_user_comment(self):
        new_post = Post.objects.create(author=self.second_user,
                                       group=self.group,
                                       text='post for comments')
        anon_comment = self.unauthorized_client.post(
            reverse('add_comment', args=[self.second_user, new_post.id]),
            {'text': 'comment from anon'},
            follow=True)
        self.assertEqual(new_post.comments.count(), 0,
                         "Защита от незалогиненого комментатора не сработала")

    def test_auth_user_comment(self):
        new_post = Post.objects.create(author=self.second_user,
                                       group=self.group,
                                       text='post for comments')
        auth_comment = self.authorized_client.post(
            reverse('add_comment', args=[self.second_user, new_post.id]),
            {'text': 'comment from auth'},
            follow=True)
        commented_post = self.authorized_client.get(
            reverse('post_view', args=[self.second_user, new_post.id]))
        self.assertEqual(commented_post.context['comments'][0].text,
                         'comment from auth',
                         "Получен неверный комментарий")
