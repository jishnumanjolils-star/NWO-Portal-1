from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('te/<int:te_id>/', views.te_dashboard, name='te_dashboard'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Cable URLs
    path('cables/', views.CableListView.as_view(), name='cable_list'),
    path('cables/add/', views.CableCreateView.as_view(), name='cable_create'),
    path('cables/<int:pk>/', views.CableDetailView.as_view(), name='cable_detail'),
    path('cables/<int:pk>/edit/', views.CableUpdateView.as_view(), name='cable_update'),
    path('cables/<int:pk>/delete/', views.CableDeleteView.as_view(), name='cable_delete'),
    
    # Equipment URLs
    path('equipment/', views.EquipmentListView.as_view(), name='equipment_list'),
    path('equipment/add/', views.EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<int:pk>/', views.EquipmentDetailView.as_view(), name='equipment_detail'),
    path('equipment/<int:pk>/edit/', views.EquipmentUpdateView.as_view(), name='equipment_update'),
    path('equipment/<int:pk>/delete/', views.EquipmentDeleteView.as_view(), name='equipment_delete'),
    
    # Circuit URLs
    path('circuits/', views.CircuitListView.as_view(), name='circuit_list'),
    path('circuits/add/', views.CircuitCreateView.as_view(), name='circuit_create'),
    path('circuits/<int:pk>/', views.CircuitDetailView.as_view(), name='circuit_detail'),
    path('circuits/<int:pk>/edit/', views.CircuitUpdateView.as_view(), name='circuit_update'),
    path('circuits/<int:pk>/delete/', views.CircuitDeleteView.as_view(), name='circuit_delete'),
    path('circuits/clear/', views.clear_circuits, name='clear_circuits'),
    
    # BTS URLs
    path('bts/', views.BTSListView.as_view(), name='bts_list'),
    path('bts/create/', views.BTSCreateView.as_view(), name='bts_create'),
    path('bts/<int:pk>/', views.BTSDetailView.as_view(), name='bts_detail'),
    path('bts/<int:pk>/edit/', views.BTSUpdateView.as_view(), name='bts_update'),
    path('bts/<int:pk>/delete/', views.BTSDeleteView.as_view(), name='bts_delete'),
    
    # No 4G BTS URLs
    path('bts/no-4g/', views.No4GBTSListView.as_view(), name='no_4g_bts_list'),
    path('bts/no-4g/create/', views.No4GBTSCreateView.as_view(), name='no_4g_bts_create'),
    path('bts/no-4g/<int:pk>/', views.No4GBTSDetailView.as_view(), name='no_4g_bts_detail'),
    path('bts/no-4g/<int:pk>/edit/', views.No4GBTSUpdateView.as_view(), name='no_4g_bts_update'),
    path('bts/no-4g/<int:pk>/delete/', views.No4GBTSDeleteView.as_view(), name='no_4g_bts_delete'),
    
    # FTTH URLs
    path('ftth/', views.FTTHListView.as_view(), name='ftth_list'),
    path('ftth/add/', views.FTTHCreateView.as_view(), name='ftth_create'),
    path('ftth/<int:pk>/', views.FTTHDetailView.as_view(), name='ftth_detail'),
    path('ftth/<int:pk>/edit/', views.FTTHUpdateView.as_view(), name='ftth_update'),
    path('ftth/<int:pk>/delete/', views.FTTHDeleteView.as_view(), name='ftth_delete'),
    
    # LIU URLs
    path('te/<int:te_id>/liu-setup/', views.te_liu_setup, name='te_liu_setup'),
    path('te/<int:te_id>/jb-routes/', views.te_jb_routes, name='te_jb_routes'),
    path('liu/', views.LIUListView.as_view(), name='liu_list'),
    path('liu/add/', views.LIUCreateView.as_view(), name='liu_create'),
    path('liu/<int:pk>/edit/', views.LIUUpdateView.as_view(), name='liu_edit'),
    path('liu/<int:liu_id>/', views.liu_detail, name='liu_detail'),
    
    # Junction Box URLs
    path('jb/', views.JBListView.as_view(), name='jb_list'),
    path('jb/add/', views.JBCreateView.as_view(), name='jb_create'),
    path('jb/<int:pk>/', views.JBDetailView.as_view(), name='jb_detail'),
    path('jb/<int:pk>/edit/', views.JBUpdateView.as_view(), name='jb_update'),
    path('jb/<int:pk>/delete/', views.JBDeleteView.as_view(), name='jb_delete'),
    path('jb/<int:jb_id>/splicing/', views.jb_splicing, name='jb_splicing'),
    
    # API
    path('api/cable/<int:cable_id>/fibers/', views.api_get_fibers, name='api_get_fibers'),
    path('api/cable/<int:cable_id>/details/', views.get_cable_details, name='get_cable_details'),
    
    # Analytics & Reports
    path('analytics/', views.analytics, name='analytics'),
    path('analytics/export/', views.export_analytics, name='export_analytics'),
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('download-template/', views.download_template, name='download_template'),
    path('export/cables/', views.export_cables, name='export_cables'),
    path('export/equipment/', views.export_equipment, name='export_equipment'),
    path('export/bts/', views.export_bts, name='export_bts'),
    path('export/bts/no-4g/', views.export_no_4g_bts, name='export_no_4g_bts'),
    path('export/ftth/', views.export_ftth, name='export_ftth'),
    path('export/circuits/', views.export_circuits, name='export_circuits'),

    # OH Maintenance Module
    path('oh-maintenance/', views.OHMaintenanceListView.as_view(), name='oh_maintenance_list'),
    path('oh-maintenance/add/', views.OHMaintenanceCreateView.as_view(), name='oh_maintenance_create'),
    path('oh-maintenance/<int:pk>/', views.OHMaintenanceDetailView.as_view(), name='oh_maintenance_detail'),
    path('oh-maintenance/<int:pk>/edit/', views.OHMaintenanceUpdateView.as_view(), name='oh_maintenance_update'),
    path('oh-maintenance/<int:pk>/delete/', views.OHMaintenanceDeleteView.as_view(), name='oh_maintenance_delete'),
    path('oh-maintenance/bill/', views.oh_maintenance_bill, name='oh_maintenance_bill'),
    path('oh-maintenance/dashboard/', views.oh_maintenance_dashboard, name='oh_maintenance_dashboard'),
    
    # OH Rate Master
    path('oh-rate-master/', views.OHMaintenanceRateMasterListView.as_view(), name='oh_rate_master_list'),
    path('oh-rate-master/add/', views.OHMaintenanceRateMasterCreateView.as_view(), name='oh_rate_master_create'),
    
    # API for OH Maintenance
    path('api/oh-maintenance/rates/', views.get_activity_rates, name='api_oh_rates'),

    # Database Backup & Restore Facility
    path('db-management/', views.db_management, name='db_management'),
    path('db-management/backup/', views.db_backup, name='db_backup'),
    path('db-management/restore/', views.db_restore, name='db_restore'),
]
