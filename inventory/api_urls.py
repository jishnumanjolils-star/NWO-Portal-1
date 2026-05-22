from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'nwo', api.NWOViewSet, basename='nwo')
router.register(r'exchanges', api.TelephoneExchangeViewSet, basename='exchange')
router.register(r'cables', api.CableViewSet, basename='cable')
router.register(r'equipment', api.EquipmentViewSet, basename='equipment')
router.register(r'circuits', api.EBCircuitViewSet, basename='circuit')
router.register(r'bts', api.MobileBTSViewSet, basename='bts')
router.register(r'jb', api.JunctionBoxViewSet, basename='jb')
router.register(r'liu', api.LIUViewSet, basename='liu')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', api.api_dashboard, name='api_dashboard'),
    path('cable-summary/', api.api_cable_summary, name='api_cable_summary'),
    path('equipment-summary/', api.api_equipment_summary, name='api_equipment_summary'),
    path('bts-summary/', api.api_bts_summary, name='api_bts_summary'),
]