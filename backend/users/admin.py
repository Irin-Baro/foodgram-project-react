from django.contrib import admin

from .models import Subscription, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Отображение модели User в админке."""

    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_display_links = ('username',)
    search_fields = ('email', 'username',)
    filter_horizontal = ('favorite_recipes', 'shopping_cart_recipes')
    list_filter = ('username', 'email')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Отображение модели Subscription в админке."""

    list_display = ('user', 'author')
    search_fields = ('user__username', 'author__username')
