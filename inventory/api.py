from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, F, Q
from .models import NWO, TelephoneExchange, Cable, Equipment, EBCircuit, MobileBTS, JunctionBox, LIU
from .serializers import (
    NWOSerializer, TelephoneExchangeSerializer, CableSerializer,
    EquipmentSerializer, EBCircuitSerializer, MobileBTSSerializer,
    JunctionBoxSerializer, LIUSerializer
)

class DivisionFilterMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'profile') and self.request.user.profile.division:
                division = self.request.user.profile.division
                # Filter based on the model type
                model = self.queryset.model
                if model == TelephoneExchange:
                    queryset = queryset.filter(nwo=division)
                elif model == Cable:
                    queryset = queryset.filter(te__nwo=division)
                elif model == Equipment:
                    queryset = queryset.filter(te__nwo=division)
                elif model == EBCircuit:
                    queryset = queryset.filter(te__nwo=division)
                elif model == MobileBTS:
                    queryset = queryset.filter(maan_node__te__nwo=division)
                elif model == JunctionBox:
                    queryset = queryset.filter(te__nwo=division)
                elif model == LIU:
                    queryset = queryset.filter(te__nwo=division)
        return queryset

class NWOViewSet(viewsets.ModelViewSet):
    queryset = NWO.objects.all()
    serializer_class = NWOSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = NWO.objects.all()
        if not self.request.user.is_superuser:
            if hasattr(self.request.user, 'profile') and self.request.user.profile.division:
                queryset = queryset.filter(id=self.request.user.profile.division.id)
        return queryset

class TelephoneExchangeViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = TelephoneExchange.objects.select_related('nwo').all()
    serializer_class = TelephoneExchangeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        nwo_id = self.request.query_params.get('nwo')
        if nwo_id:
            queryset = queryset.filter(nwo_id=nwo_id)
        return queryset

class CableViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = Cable.objects.select_related('te', 'te__nwo').all()
    serializer_class = CableSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by cable type
        cable_type = self.request.query_params.get('cable_type')
        if cable_type:
            queryset = queryset.filter(cable_type=cable_type)
        
        # Filter by mode (OH/UG)
        mode = self.request.query_params.get('mode')
        if mode:
            queryset = queryset.filter(mode=mode)
        
        # Filter by TE
        te_id = self.request.query_params.get('te')
        if te_id:
            queryset = queryset.filter(te_id=te_id)
        
        return queryset

class EquipmentViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = Equipment.objects.select_related('te', 'te__nwo').all()
    serializer_class = EquipmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by equipment type
        eq_type = self.request.query_params.get('equipment_type')
        if eq_type:
            queryset = queryset.filter(equipment_type=eq_type)
        
        # Filter by TE
        te_id = self.request.query_params.get('te')
        if te_id:
            queryset = queryset.filter(te_id=te_id)
        
        return queryset

class EBCircuitViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = EBCircuit.objects.select_related('te', 'te__nwo', 'cable', 'equipment').all()
    serializer_class = EBCircuitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by circuit type
        circuit_type = self.request.query_params.get('circuit_type')
        if circuit_type:
            queryset = queryset.filter(circuit_type=circuit_type)
        
        # Filter by TE
        te_id = self.request.query_params.get('te')
        if te_id:
            queryset = queryset.filter(te_id=te_id)
        
        return queryset

class MobileBTSViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = MobileBTS.objects.select_related('maan_node', 'maan_node__te').all()
    serializer_class = MobileBTSSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by ring status
        is_ring = self.request.query_params.get('is_ring')
        if is_ring:
            queryset = queryset.filter(is_ring=is_ring == 'true')
        
        return queryset

class JunctionBoxViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = JunctionBox.objects.select_related('te', 'te__nwo').all()
    serializer_class = JunctionBoxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by mode (OH/UG)
        mode = self.request.query_params.get('mode')
        if mode:
            queryset = queryset.filter(mode=mode)
        
        # Filter by TE
        te_id = self.request.query_params.get('te')
        if te_id:
            queryset = queryset.filter(te_id=te_id)
        
        return queryset

class LIUViewSet(DivisionFilterMixin, viewsets.ModelViewSet):
    queryset = LIU.objects.select_related('te', 'te__nwo', 'cable').all()
    serializer_class = LIUSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by TE
        te_id = self.request.query_params.get('te')
        if te_id:
            queryset = queryset.filter(te_id=te_id)
        
        return queryset

# Dashboard API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_dashboard(request):
    """Dashboard summary API"""
    division = None
    if not request.user.is_superuser:
        if hasattr(request.user, 'profile') and request.user.profile.division:
            division = request.user.profile.division

    nwos = NWO.objects.annotate(te_count=Count('exchanges'))
    if division:
        nwos = nwos.filter(id=division.id)
    
    exchanges = TelephoneExchange.objects.all()
    cables = Cable.objects.all()
    equipment = Equipment.objects.all()
    circuits = EBCircuit.objects.all()
    bts = MobileBTS.objects.all()
    jbs = JunctionBox.objects.all()
    lius = LIU.objects.all()

    if division:
        exchanges = exchanges.filter(nwo=division)
        cables = cables.filter(te__nwo=division)
        equipment = equipment.filter(te__nwo=division)
        circuits = circuits.filter(te__nwo=division)
        bts = bts.filter(maan_node__te__nwo=division)
        jbs = jbs.filter(te__nwo=division)
        lius = lius.filter(te__nwo=division)

    data = {
        'total_nwo': nwos.count(),
        'total_te': exchanges.count(),
        'total_cables': cables.count(),
        'total_equipment': equipment.count(),
        'total_circuits': circuits.count(),
        'total_bts': bts.count(),
        'total_jb': jbs.count(),
        'total_liu': lius.count(),
        'nwos': NWOSerializer(nwos, many=True).data,
    }
    return Response(data)

# Cable Summary API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_cable_summary(request):
    """Cable summary by type and mode"""
    division = None
    if not request.user.is_superuser:
        if hasattr(request.user, 'profile') and request.user.profile.division:
            division = request.user.profile.division

    oh_queryset = Cable.objects.filter(mode='OH')
    ug_queryset = Cable.objects.filter(mode='UG')

    if division:
        oh_queryset = oh_queryset.filter(te__nwo=division)
        ug_queryset = ug_queryset.filter(te__nwo=division)

    oh_summary = oh_queryset.values('cable_type').annotate(count=Count('id'))
    ug_summary = ug_queryset.values('cable_type').annotate(count=Count('id'))
    
    return Response({
        'oh_cables': list(oh_summary),
        'ug_cables': list(ug_summary),
    })

# Equipment Summary API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_equipment_summary(request):
    """Equipment summary by type"""
    division = None
    if not request.user.is_superuser:
        if hasattr(request.user, 'profile') and request.user.profile.division:
            division = request.user.profile.division

    queryset = Equipment.objects.all()
    if division:
        queryset = queryset.filter(te__nwo=division)

    summary = queryset.values('equipment_type').annotate(
        total=Count('id'),
        total_ports=Sum('total_ports'),
        used_ports=Sum('used_ports')
    )
    return Response({'equipment_summary': list(summary)})

# BTS Summary API
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_bts_summary(request):
    """Mobile BTS summary by RP ID"""
    division = None
    if not request.user.is_superuser:
        if hasattr(request.user, 'profile') and request.user.profile.division:
            division = request.user.profile.division

    bts_list = MobileBTS.objects.select_related('maan_node', 'maan_node__te').all()
    if division:
        bts_list = bts_list.filter(maan_node__te__nwo=division)

    return Response({
        'total': bts_list.count(),
        'bts': MobileBTSSerializer(bts_list, many=True).data
    })