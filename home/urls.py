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
    path('contact/' , ContactView.as_view() , name='contact'),
    path('thanks/', lambda request: render(request, 'thanks.html'), name='thanks'),
    path('conditioners/<int:pk>/comment/', add_comment, name='conditioner-comments'),
    path('comment/<int:pk>/update/', update_comment, name='update-comment'),
    path('comment/<int:pk>/delete/', delete_comment, name='delete-comment'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='update-profile'),
    path('append/', PostCreateView.as_view(), name='conditioner-create'),
    path('korzinka/', KorzinkaView.as_view(), name='korzinka'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('remove-from-cart/<int:pk>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('decrease-quantity/<int:pk>/', DecreaseQuantityView.as_view(), name='decrease-quantity'),
    path('increase-quantity/<int:pk>/', IncreaseQuantityView.as_view(), name='increase-quantity'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/', PaymentView.as_view(), name='payment'),
    path('process-payment/', process_payment, name='process-payment'),
    path('order-confirmation/<int:pk>/', OrderConfirmationView.as_view(), name='order_confirmation'),
    path('about/' , about , name='about')
]
