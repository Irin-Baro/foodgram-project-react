from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        unique=True,
        validators=(validate_username,),
        max_length=150,
        verbose_name='Юзернейм',
        help_text='Укажите юзернейм',
    )
    email = models.EmailField(
        unique=True,
        max_length=150,
        verbose_name='email',
        help_text='Укажите адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Имя',
        help_text='Укажите имя',

    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Фамилия',
        help_text='Укажите фамилию',
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        verbose_name='Пароль',
        help_text='Введите пароль',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
        help_text='Укажите пользователя, который хочет подписаться',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор',
        help_text='Укажите автора, на которого хотите подписаться',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_followers'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='not_subscribe_to_self'
            )
        )
        ordering = ('-id',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
