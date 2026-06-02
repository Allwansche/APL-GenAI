from django.urls import path
from .views import MealPlanListCreateAPIView, MealPlanRetrieveDestroyAPIView, index_view, standalone_view

urlpatterns = [
    # API endpoints
    path('api/plans/', MealPlanListCreateAPIView.as_view(), name='plan-list-create'),
    path('api/plans/<int:pk>/', MealPlanRetrieveDestroyAPIView.as_view(), name='plan-retrieve-destroy'),
    
    # Frontend SPA served from app root or template
    path('', index_view, name='index'),
    path('standalone/', standalone_view, name='standalone'),
]
