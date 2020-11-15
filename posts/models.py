from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):

    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts"
                               )
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              related_name="posts_group",
                              null=True,
                              blank=True
                              )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return f'{self.author} - {self.pub_date} - {self.group} - {self.image}'

    class Meta:

        ordering = ["-pub_date", ]


class Comment(models.Model):
    author = models.ForeignKey(User,
                               related_name='comments',
                               on_delete=models.CASCADE)
    post = models.ForeignKey(Post,
                             related_name='comments',
                             on_delete=models.CASCADE)
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return f'{self.author} - {self.post} - {self.created}'

    class Meta:

        ordering = ["-created", ]


class Follow(models.Model):

    user = models.ForeignKey(User,
                             related_name='follower',
                             on_delete=models.CASCADE)
    author = models.ForeignKey(User,
                               related_name='following',
                               on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} follower of {self.author}'
