from django.urls import path
from . import views

app_name = 'userauths'

urlpatterns = [
    path('sign-up/',views.register,name='sign-up'),
    path('vendor_register/', views.register_vendor, name='vendor_register'),
    path('custom_login/',views.custom_login,name='custom_login'),
    path('custom_logout/',views.custom_logout,name='custom_logout'), 
    path('activate/<uidb64>/<token>',views.ActivateAccountView.as_view(),name='customeractivate'),
    path('activate/<uidb64>/<token>',views.VendorActivateAccountView.as_view(),name='vendoractivate'), 
    path('request_reset_email/',views.RequestResetEmailView.as_view(),name='request_reset_email'),
    path('set_new_password/<uidb64>/<token>',views.SetNewPasswordView.as_view(),name='set_new_password'),
     path('profile_update/',views.profile_update,name='profile_update'),

]