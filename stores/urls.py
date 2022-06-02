from django.urls import path

from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('search/',views.search, name='search'),
    path('category/',views.category, name='category'),
    path('singleproduct/<slug:slug>/',views.singleproduct, name='singleproduct'),
    path('addtocart/<str:id>/',views.addtocart,name='addtocart'),
    path('myCart',views.myCart,name='myCart'),
    path('manageCart/<str:id>/',views.manageCart,name='manageCart'),
    path('manageCart/<str:id>/',views.manageCart,name='manageCart'),
    path('emptyCart',views.emptyCart,name='emptyCart'),
    path('checkout',views.checkout,name='checkout'),
    path('transfer/<int:id>/',views.transfer,name='transfer'),

    path('payment/<int:id>/',views.paymentPage,name='payment'),
    path('<str:ref>/',views.verify_payment,name='verify-payment'),
   
]