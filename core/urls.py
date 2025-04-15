from django.urls import path, include
from core import views


urlpatterns = [
    # Home url
    path('',views.Home, name='Home'),
    path('Not_Found/',views.Not_Found, name='Not_Found'),

    # Store url
    path('Store/',views.product_list_view, name='product_list_view'),

    # Product Detail url
    path('single_product/<pid>/<slug:slug>/',views.product_detail_view, name='product_detail_view'),
    
    # Seller url
    path('All_vendors/',views.All_vendors, name='All_vendors'),

    # Categories
    path('category/',views.Category_list_view, name='Category_list_view'),
    path('category/<int:id>/<slug:slug>/',views.product_by_category, name='product_by_category'),
    path('subcategory/<int:category_id>/<slug:category_slug>/', views.subcategory_view, name='subcategory_view'),

    
    path('products/tag/<slug:tag_slug>/', views.tag_list, name='tags'),

    path("ajax-add-review/<pid>/",views.ajax_add_review, name="ajax-add-review"),
    path("search/", views.search_view, name="search"),
    path("filter-products/", views.filter_product, name="filter-product"),
    path("add_to_cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("delete_from_cart/", views.delete_from_cart, name="delete_from_cart"),
    path("update_cart/", views.update_cart, name="update_cart"),
    path('set-currency/<str:currency_code>/', views.set_currency, name='set_currency'),
    path("checkout/", views.checkout, name="checkout"),
    #path("save_checkout_info/", views.save_checkout_info, name="save_checkout_info"),
    
    path('payment_view/<oid>/', views.payment_view, name='payment_view'),
    path('place_order/', views.place_order, name="place_order"),
    #path('save_payment_method/', views.save_payment_method, name='save_payment_method'),


    # paypal url
    path("paypal/", include('paypal.standard.ipn.urls')),
    path("payment_completed_view/<oid>/", views.payment_completed_view, name="payment_completed_view"),
    path('payment_failed_view/<str:oid>/', views.payment_failed_view, name='payment_failed_view'),
    path("order_confirmation/<oid>/", views.order_confirmation, name="order_confirmation"),
    path("dashboard/",views.dashboard, name="dashboard"),
    path("dashboard/order/<int:id>",views.order_detail, name="order_detail"),

    # Making date Default
    path("make_address_default/",views.make_address_default, name="make_address_default"),

    # wishlist Page 
    path("wishlist_view/",views.wishlist_view, name="wishlist_view"),
    path("add_to_wishlist/",views.add_to_wishlist, name="add_to_wishlist"),


    # Remove from Wishlist
    path("remove_wishlist/",views.remove_wishlist, name="remove_wishlist"),
    #path('calculate-shipping-fee/', views.calculate_shipping_fee, name='calculate_shipping_fee'),

    # Contact Us Page 
    path("contact/", views.contact, name="contact"),
    path("ajax_contact/", views.ajax_contact, name="ajax_contact"),

    #Platform Settings
    #frequently asked Questions
    path('faq/', views.faq, name='faq'),
    path('policy_privacy/', views.policy_privacy, name='policy_privacy'),
    path('Why_sellonEmariStore/', views.why, name='why'),
    path('return_policy/', views.return_policy, name='return_policy'),

    # Vendor Urls 

    path('vendor_detail/<vid>/', views.vendor_detail_view, name='vendor_detail_view'),
    path('vendor_list/', views.vendor_list, name='vendor_list'),
    path('account_orders_view/', views.account_orders_view, name='account_orders_view'),
    
    

]

