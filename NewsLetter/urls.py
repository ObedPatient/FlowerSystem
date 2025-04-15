from django.urls import path
from . import views
from .views import ProductSitemap
from .views import custom_404_view
from django.contrib.sitemaps.views import sitemap

# urls.py
handler404 = custom_404_view

sitemaps = {
    'products': ProductSitemap,
}


urlpatterns = [
    path('subscribe/', views.subscribe, name='subscribe'),
    path('collect_user_details/', views.collect_user_details, name='collect_user_details'),
    path('get_username/', views.get_username, name='get_username'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
    path('terms_services/', views.terms_services, name='terms_services'),
    path('approach/', views.approach, name='approach'),
    path('ourCompany/', views.ourCompany, name='ourCompany'),
    path('track_order/', views.track_order, name='track_order'),
    path('about_us/', views.about_us, name='about_us'),

]


