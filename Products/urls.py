from django.urls import path
from . import views



urlpatterns = [
    path('save/physical/', views.save_physical, name='save_physical'),
    path('save/digital/', views.save_digital, name='save_digital'),
    path('save/course/', views.save_course, name='save_course'),
    path('save/service/', views.save_service, name='save_service'),
    path('', views.product_page, name='product'),
    path('add-category-ajax/', views.add_category_ajax, name='add_category_ajax'),
    
    path('products/physical/update/', views.update_physical, name='update_physical'),
    path('products/digital/update/', views.update_digital, name='update_digital'),
    path('products/course/update/', views.update_course, name='update_course'),
    path('products/service/update/', views.update_service, name='update_service'),
    
    path('delete/<int:pk>/<str:product_type>/',views.delete_product,name='delete_product'),

]
