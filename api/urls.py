from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TravelProjectViewSet, PlaceViewSet, UserRegistrationView

router = DefaultRouter()
router.register(r'projects', TravelProjectViewSet, basename='project')
router.register(r'places', PlaceViewSet, basename='place')

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('', include(router.urls)),
]
