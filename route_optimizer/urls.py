from django.urls import path
from .views import OptimalRouteView

urlpatterns = [
    path('optimize/', OptimalRouteView.as_view(), name='optimize-route'),
]

