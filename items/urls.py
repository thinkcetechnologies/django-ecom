from django.urls import path
from .views  import index, detail, add_to_cart, remove_from_cart,OrderSummaryView,remove_one_from_cart,Checkout,PaymentForm


urlpatterns=[
    path('',index.as_view(),name="index"),
    path('details/<slug>/', detail,name="detail"),
    path('order-summary/', OrderSummaryView.as_view(),name="order-summary"),
    # path('payment/stripe/', PaymentView.as_view(),name="stripe"),
    path('checkout/', Checkout.as_view(),name="checkout"),
    path('add-to-cart/<slug>/',add_to_cart,name='add-to-cart'),
    path('remove-from-cart/<slug>/',remove_from_cart,name='remove-from-cart'),
    path('remove-one-from-cart/<slug>/',remove_one_from_cart, name='remove-one-from-cart'),
]