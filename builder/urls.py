from django.urls import path
from . import views

app_name = 'builder'
urlpatterns = [
    path('', views.builder_dashboard, name='dashboard'),
    path('schema.json', views.export_schema, name='schema'),
    path('types/<int:type_id>/config/', views.save_type_config, name='save_type_config'),
    path('types/<int:type_id>/reorder-fields/', views.reorder_fields, name='reorder_fields'),
    path('types/<int:type_id>/layout/', views.save_type_layout, name='save_type_layout'),
    path('fields/<int:field_id>/config/', views.save_field_config, name='save_field_config'),
    path('snapshots/create/', views.create_snapshot, name='create_snapshot'),
    path('snapshots/<int:snapshot_id>/rollback/', views.rollback_snapshot, name='rollback_snapshot'),
    path('generate-project/', views.generate_project, name='generate_project'),
]
