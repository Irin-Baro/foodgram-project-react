from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet, basename='ingredient')
router.register('recipes', views.RecipeViewSet, basename='recipe')
router.register('tags', views.TagViewSet, basename='tag')
router.register('users', views.CustomUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
