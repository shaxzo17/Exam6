from django.urls import path
from .views import *
urlpatterns = [
    path('' , home , name='home'),
    path('conditioners/' , CondListView.as_view() , name='conditioners'),
    path('append/' , CondCreateView.as_view() , name='conditioner-create'),
    path('conditioners/<int:pk>/', CondDetailView.as_view(), name='conditioner-detail'),
    path('conditioner-update/<int:pk>/' , CondUpdateView.as_view() , name='conditioner-update'),
    path('conditioner-delete/<int:pk>/' , CondDeleteView.as_view() , name='conditioner-delete'),
    path('add-to-cart/<int:pk>/', AddCartView.as_view(), name='add-to-cart'),
    path('korzinka/', KorzinkaView.as_view(), name='korzinka'),
    path('contact/' , ContactView.as_view() , name='contact'),
    path('thanks/', lambda request: render(request, 'thanks.html'), name='thanks'),
]