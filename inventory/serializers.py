from rest_framework import serializers
from .models import NWO, TelephoneExchange, Cable, Fiber, Equipment, EBCircuit, MobileBTS, JunctionBox, LIU, LIUPort, Splicing

class NWOSerializer(serializers.ModelSerializer):
    class Meta:
        model = NWO
        fields = '__all__'

class TelephoneExchangeSerializer(serializers.ModelSerializer):
    nwo_name = serializers.CharField(source='nwo.name', read_only=True)
    
    class Meta:
        model = TelephoneExchange
        fields = '__all__'

class FiberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fiber
        fields = '__all__'

class CableSerializer(serializers.ModelSerializer):
    te_name = serializers.CharField(source='te.name', read_only=True)
    fiber_count = serializers.IntegerField(read_only=True)
    fibers = FiberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cable
        fields = '__all__'

class EquipmentSerializer(serializers.ModelSerializer):
    te_name = serializers.CharField(source='te.name', read_only=True)
    port_utilization = serializers.SerializerMethodField()
    
    class Meta:
        model = Equipment
        fields = '__all__'
    
    def get_port_utilization(self, obj):
        if obj.total_ports > 0:
            return f"{int(obj.used_ports / obj.total_ports * 100)}%"
        return "0%"

class EBCircuitSerializer(serializers.ModelSerializer):
    te_name = serializers.CharField(source='te.name', read_only=True)
    cable_name = serializers.CharField(source='cable.name', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    
    class Meta:
        model = EBCircuit
        fields = '__all__'

class MobileBTSSerializer(serializers.ModelSerializer):
    maan_node_name = serializers.CharField(source='maan_node.name', read_only=True)
    te_name = serializers.CharField(source='maan_node.te.name', read_only=True)
    
    class Meta:
        model = MobileBTS
        fields = '__all__'

class LIUPortSerializer(serializers.ModelSerializer):
    fiber_number = serializers.IntegerField(source='fiber.fiber_number', read_only=True)
    
    class Meta:
        model = LIUPort
        fields = '__all__'

class LIUSerializer(serializers.ModelSerializer):
    te_name = serializers.CharField(source='te.name', read_only=True)
    cable_name = serializers.CharField(source='cable.name', read_only=True)
    ports = LIUPortSerializer(many=True, read_only=True)
    
    class Meta:
        model = LIU
        fields = '__all__'

class SplicingSerializer(serializers.ModelSerializer):
    fiber_in_detail = serializers.SerializerMethodField()
    fiber_out_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = Splicing
        fields = '__all__'
    
    def get_fiber_in_detail(self, obj):
        return f"{obj.fiber_in.cable.name} - Fiber {obj.fiber_in.fiber_number}"
    
    def get_fiber_out_detail(self, obj):
        return f"{obj.fiber_out.cable.name} - Fiber {obj.fiber_out.fiber_number}"

class JunctionBoxSerializer(serializers.ModelSerializer):
    te_name = serializers.CharField(source='te.name', read_only=True)
    splices = SplicingSerializer(many=True, read_only=True)
    
    class Meta:
        model = JunctionBox
        fields = '__all__'