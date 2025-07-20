from django.urls import path, include
from .import views
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'leads', views.LeadViewSet)
urlpatterns = [
    
    path('api/leads/',views.lead_list_create, name='lead-list-create'),
    
    path('',views.home,name='home'),
    path('api/', include(router.urls)),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path('client_dashboard/',views.client_dashboard, name='client_dashboard'),
   
    path('createlead/',views.createlead, name='createlead'),
    path('lead_update/<int:lead_id>/',views.lead_update, name='lead_update'),
    path('lead_delete/<int:lead_id>/',views.lead_delete, name='lead_delete'),
    path('lead_detail/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('client_create_staff/',views. client_create_staff, name='client_create_staff'),
    path('staff_list/',views. staff_list, name='staff_list'),
    #path('staff_update/<int:staff_id>/',views.staff_update, name='staff_update'), 
    path('profilesettings/',views.profilesettings,name='profilesettings'),
    path("profile/",views.user_profile, name="profile"),
    path('client_home/', views.client_home, name='client_home'),
    
    path("staff/edit/<int:staff_id>/",views.edit_staff, name="edit_staff"),
    path("staff/delete/<int:staff_id>/",views.delete_staff, name="delete_staff"),
    #path('search/',views.search_view, name='search'), 
    path('search/', views.search, name='search'),
    path('base/',views.base, name='base'),
    
    path('kanban_view/',views.kanban_view, name='kanban_view'),
 
    path('leads/<int:lead_id>/get_details/', views.get_lead, name='get_lead'),

    path("update_lead_status/<int:lead_id>/",views.update_lead_status, name="update_lead_status"),
    path("update-lead/<int:lead_id>/",views.update_lead, name="update_lead"),
   
    
    path("client_won/",views.client_won, name="client_won"),
    
    path('assign_user_to_tenant/',views.assign_user_to_tenant, name='assign_user_to_tenant'),
    
    path('lead/<int:lead_id>/send_email/', views.send_email, name='send_email'),
    
    path('create_custom_column/', views.create_custom_column, name='create_custom_column'),
    path('',views.tenant_home, name='tenant-home'),
    
    path('create_board/', views.create_board, name='create_board'),
    path('board_details/<int:board_id>/', views.board_details, name='board_details'),
    path('create_column/<int:board_id>/', views.create_column, name='create_column'),
    
    path('board_list/', views.board_list, name='board_list'),
    
    path('pipeline/', views.pipeline, name='pipeline'),
    
    path('ajax/add_column/<int:board_id>/', views.ajax_add_column, name='ajax_add_column'),
    
    path('ajax/add_card/<int:column_id>/', views.add_card, name='add_card'),
    
    path('ajax/move_card/', views.move_card, name='move_card'),
    
    path('ajax/card_detail/<int:card_id>/', views.ajax_card_detail, name='ajax_card_detail'),


    # urls.py
    path('leads/<int:lead_id>/update-description/', views.update_lead_description, name='update_lead_description'),
    
    path('api/all-products/',views.all_products_json, name='all-products-json'),
    path('leads/<int:lead_id>/get_details/', views.get_lead_details, name='get_details'),
    path('leads/<int:lead_id>/update_fields/', views.update_lead_fields, name='update_lead_fields'),

    

]   