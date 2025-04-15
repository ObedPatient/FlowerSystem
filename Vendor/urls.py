from django.urls import path, include
from Vendor import views


urlpatterns = [
    path('vendorProducts/', views.vendorProducts, name="vendorProducts"),
    path('product/<pid>/', views.product_details, name='product_details'),
    path('vendorOrders/', views.vendorOrders, name="vendorOrders"),
    path('vendorStore/', views.vendorStore, name="vendorStore"),
    path('vendorAddCategory/', views.vendorAddCategory, name='vendorAddCategory'),
    path('vendorDashboard/', views.vendorDashboard, name="vendorDashboard"), 
    path('vendorChangepswd/', views.vendorChangepswd, name="vendorChangepswd"),
    path('vendor_order_Details/<int:vendor_order_id>/', views.vendor_order_Details, name="vendor_order_Details"),
    path('vendor_orders_view/', views.vendor_orders_view, name='vendor_orders_view'),
    path('export_vendor_orders_excel/', views.export_vendor_orders_excel, name='export_vendor_orders_excel'),
    path('search_vendor/', views.search_vendor, name='search_vendor'),
    path("vendor_product/", views.vendor_product, name='vendor_product'),
    path('InStoreOrder/', views.InStoreOrder, name='InStoreOrder'),
]
