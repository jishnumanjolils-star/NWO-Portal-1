from django.contrib import admin
from .models import NWO, TelephoneExchange, Cable, Fiber, Equipment, EBCircuit, MobileBTS, JunctionBox, LIU, CableRoutePoint, UserProfile, FTTH, OHMaintenanceEntry, OHMaintenanceActivity, OHMaintenanceRateMaster

class OHMaintenanceActivityInline(admin.TabularInline):
    model = OHMaintenanceActivity
    extra = 1

@admin.register(OHMaintenanceEntry)
class OHMaintenanceEntryAdmin(admin.ModelAdmin):
    list_display = ('maintenance_date', 'team_name', 'division', 'te', 'status')
    list_filter = ('status', 'division', 'te', 'maintenance_date')
    search_fields = ('team_name', 'work_order_no', 'location', 'route_name')
    inlines = [OHMaintenanceActivityInline]
    actions = ['approve_entries', 'verify_entries']

    def approve_entries(self, request, queryset):
        queryset.update(status='Approved', approved_by=request.user)
    approve_entries.short_description = "Mark selected entries as Approved"

    def verify_entries(self, request, queryset):
        queryset.update(status='Verified', verified_by=request.user)
    verify_entries.short_description = "Mark selected entries as Verified"

@admin.register(OHMaintenanceRateMaster)
class OHMaintenanceRateMasterAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'unit_type', 'unit_rate', 'is_active', 'effective_from', 'effective_to')
    list_filter = ('is_active', 'activity_type')
    search_fields = ('activity_type',)

@admin.register(FTTH)
class FTTHAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'landline_number', 'olt_name', 'port_number', 'division')
    list_filter = ('division', 'port_number')
    search_fields = ('customer_name', 'landline_number', 'olt_name')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'per_no', 'designation', 'division', 'force_password_change', 'last_password_reset')
    list_filter = ('division', 'designation', 'force_password_change')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'per_no')
    readonly_fields = ('last_password_reset',)

@admin.register(CableRoutePoint)
class CableRoutePointAdmin(admin.ModelAdmin):
    list_display = ('cable', 'order', 'latitude', 'longitude')
    list_filter = ('cable',)
    search_fields = ('cable__name',)
# from import_export.admin import ImportExportModelAdmin

@admin.register(NWO)
class NWOAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(TelephoneExchange)
class TelephoneExchangeAdmin(admin.ModelAdmin):
    list_display = ('name', 'nwo')
    list_filter = ('nwo',)
    search_fields = ('name',)

@admin.register(Cable)
class CableAdmin(admin.ModelAdmin):
    list_display = ('name', 'cable_type', 'mode', 'category', 'te')
    list_filter = ('mode', 'category', 'cable_type', 'te')
    search_fields = ('name',)

@admin.register(Fiber)
class FiberAdmin(admin.ModelAdmin):
    list_display = ('cable', 'fiber_number', 'is_used', 'status')
    list_filter = ('is_used', 'status', 'cable__name')
    search_fields = ('cable__name',)

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'equipment_type', 'te', 'used_ports', 'total_ports')
    list_filter = ('equipment_type', 'te')
    search_fields = ('name',)

@admin.register(EBCircuit)
class EBCircuitAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'circuit_type', 'bandwidth', 'te')
    list_filter = ('circuit_type', 'te')
    search_fields = ('client_name',)

@admin.register(MobileBTS)
class MobileBTSAdmin(admin.ModelAdmin):
    list_display = ('rp_id', 'maan_node', 'maan_port', 'receive_power_db')
    list_filter = ('maan_node',)
    search_fields = ('rp_id',)

@admin.register(JunctionBox)
class JunctionBoxAdmin(admin.ModelAdmin):
    list_display = ('jb_id', 'jb_name', 'cable_mode', 'jb_type', 'te', 'latitude', 'longitude', 'created_at')
    list_filter = ('cable_mode', 'jb_type', 'te', 'created_at')
    search_fields = ('jb_id', 'jb_name', 'te__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('jb_id', 'jb_name', 'te', 'cable_mode', 'jb_type')
        }),
        ('Fiber Details', {
            'fields': ('fiber_entering', 'fiber_out', 'splicing_info')
        }),
        ('Location', {
            'fields': ('landmark', 'latitude', 'longitude', 'jb_image')
        }),
        ('Cable Connections', {
            'fields': ('input_cables', 'output_cables')
        }),
        ('Additional', {
            'fields': ('remarks', 'created_at', 'updated_at')
        })
    )

@admin.register(LIU)
class LIUAdmin(admin.ModelAdmin):
    list_display = ('id', 'te', 'cable', 'capacity')
    list_filter = ('te', 'capacity')
