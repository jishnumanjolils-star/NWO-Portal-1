from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User

class NWO(models.Model):
    NAME_CHOICES = [
        ('NWO CENTRAL', 'NWO CENTRAL'),
        ('NWO PALARIVATTOM', 'NWO PALARIVATTOM'),
        ('NWO KOCHI', 'NWO KOCHI'),
        ('NWO TRIPUNITHARA', 'NWO TRIPUNITHARA'),
        ('NWO ANGAMALY', 'NWO ANGAMALY'),
        ('NWO THODUPUZHA', 'NWO THODUPUZHA'),
        ('NWO ALUVA', 'NWO ALUVA'),
        ('NWO MOOVATTUPUZHA', 'NWO MOOVATTUPUZHA'),
        ('NWO ADIMALY', 'NWO ADIMALY'),
        ('NWO KATTAPPANA', 'NWO KATTAPPANA'),
    ]
    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    per_no = models.CharField(max_length=20, unique=True, verbose_name="PER NO")
    designation = models.CharField(max_length=50)
    division = models.ForeignKey(NWO, on_delete=models.SET_NULL, null=True, blank=True)
    force_password_change = models.BooleanField(default=False)
    last_password_reset = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.per_no})"

class TelephoneExchange(models.Model):
    nwo = models.ForeignKey(NWO, on_delete=models.CASCADE, related_name='exchanges')
    name = models.CharField(max_length=100)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('nwo', 'name')

    def __str__(self):
        return f"{self.name} ({self.nwo.name})"

class Cable(models.Model):
    CABLE_TYPE_CHOICES = [
        ('288F', '288F'),
        ('96F', '96F'),
        ('48F', '48F'),
        ('24F', '24F'),
        ('12F', '12F'),
        ('4F', '4F'),
    ]
    MODE_CHOICES = [
        ('OH', 'Overhead'),
        ('UG', 'Underground'),
    ]
    CATEGORY_CHOICES = [
        ('IN', 'IN Cable'),
        ('OUT', 'OUT Cable'),
        ('TIE', 'Tie Cable'),
    ]
    STRUCTURE_CHOICES = [
        ('NORMAL', 'Normal'),
        ('RIBBON', 'Ribbon'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    transnet_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="TRANSNET ID")
    cable_type = models.CharField(max_length=10, choices=CABLE_TYPE_CHOICES)
    structure_type = models.CharField(max_length=10, choices=STRUCTURE_CHOICES, default='NORMAL', verbose_name="Cable Category")
    mode = models.CharField(max_length=2, choices=MODE_CHOICES)
    category = models.CharField(max_length=3, choices=CATEGORY_CHOICES)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.CASCADE, related_name='cables')
    connected_te = models.ForeignKey(TelephoneExchange, on_delete=models.SET_NULL, null=True, blank=True, related_name='connected_cables')
    otdr_distance = models.FloatField(null=True, blank=True, help_text="Stored in meters")
    otdr_image = models.ImageField(
        upload_to='cable_otdr_images/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])]
    )
    remarks = models.TextField() # Mandatory

    def __str__(self):
        return f"{self.name} ({self.cable_type})"

    @property
    def fiber_count(self):
        return int(self.cable_type.replace('F', ''))

    @property
    def used_fibers_count(self):
        return self.fibers.filter(
            models.Q(is_used=True) |
            ~models.Q(status='Available') |
            ~models.Q(circuit_name__in=['', None]) |
            ~models.Q(system_end__in=['', None])
        ).count()

    @property
    def available_fibers_count(self):
        return self.fiber_count - self.used_fibers_count

    @property
    def otdr_distance_formatted(self):
        if self.otdr_distance is None:
            return None
        if self.otdr_distance >= 1000:
            return f"{self.otdr_distance / 1000:g} km"
        return f"{self.otdr_distance:g} m"


class Fiber(models.Model):
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE, related_name='fibers')
    fiber_number = models.PositiveIntegerField()
    is_used = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='Available')
    circuit_name = models.CharField(max_length=255, blank=True, null=True)
    system_end = models.CharField(max_length=255, blank=True, null=True)
    otdr_distance = models.FloatField(null=True, blank=True, help_text="Stored in meters")
    otdr_image = models.ImageField(upload_to='fiber_otdr_images/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])])
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('cable', 'fiber_number')
        ordering = ['fiber_number']

    def __str__(self):
        return f"{self.cable.name} - Fiber {self.fiber_number}"

    @property
    def color(self):
        COLORS = ['Blue', 'Orange', 'Green', 'Brown', 'Slate', 'White', 'Red', 'Black', 'Yellow', 'Violet', 'Rose', 'Aqua']
        return COLORS[(self.fiber_number - 1) % 12]

    @property
    def ribbon_group(self):
        return (self.fiber_number - 1) // 12 + 1

    @property
    def otdr_distance_formatted(self):
        if self.otdr_distance is None:
            return None
        if self.otdr_distance >= 1000:
            return f"{self.otdr_distance / 1000:g} km"
        return f"{self.otdr_distance:g} m"

@receiver(post_save, sender=Cable)
def create_fibers(sender, instance, created, **kwargs):
    if created:
        count = instance.fiber_count
        fibers = [Fiber(cable=instance, fiber_number=i+1) for i in range(count)]
        Fiber.objects.bulk_create(fibers)

class Equipment(models.Model):
    TYPE_CHOICES = [
        ('CPAN', 'CPAN'),
        ('MAAN', 'MAAN'),
        ('MADM', 'MADM'),
        ('SDH_CPE', 'SDH CPE'),
        ('BSNL_OLT', 'BSNL OLT'),
        ('BBNL_OLT', 'BBNL OLT'),
        ('TIP_OLT', 'TIP OLT'),
        # Backward compatibility
        ('CPAN_B', 'CPAN B Node'),
        ('MAAN_C', 'MAAN C Node'),
        ('MAAN_A3_A4', 'MAAN A3 / A4 Node'),
        ('LCO_OLT', 'LCO OLT'),
        ('LMG', 'LMG'),
        ('NGN_SWITCH', 'NGN Switch'),
        ('MNG_PAN', 'MNG PAN'),
    ]
    equipment_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.CASCADE, related_name='equipments')
    uplink_connectivity = models.CharField(max_length=255, blank=True, null=True)
    total_ports = models.PositiveIntegerField(default=24, blank=True, null=True)
    used_ports = models.PositiveIntegerField(default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    configuration = models.JSONField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    ba = models.CharField(max_length=100, blank=True, null=True, verbose_name="BA")
    make = models.CharField(max_length=100, blank=True, null=True, verbose_name="Make")
    model_no = models.CharField(max_length=100, blank=True, null=True, verbose_name="Model")

    def __str__(self):
        return f"{self.name} ({self.get_equipment_type_display()})"

class EBCircuit(models.Model):
    NODE_CHOICES = [
        ('MEDIA_CONVERTER', 'Media Converter'),
        ('CPE', 'CPE'),
        ('A_NODE', 'A-Node'),
        ('CPAN_B', 'CPAN B-Node'),
        ('MRO_TEK', 'MRO TEK Modem'),
        ('FTTH_MODEM', 'FTTH Modem'),
        ('MADM', 'MADM'),
        ('MAAN_A3_A4', 'MAAN A3 / A4 Node'),
    ]
    CIRCUIT_TYPE_CHOICES = [
        ('INTERNET LC', 'INTERNET LC'),
        ('P2P LC', 'P2P LC'),
        ('P2P LC ACROSS STATE', 'P2P LC ACROSS STATE'),
        ('MPLS VPN', 'MPLS VPN'),
        ('ISDN PRI', 'ISDN PRI'),
    ]
    circuit_type = models.CharField(max_length=100, choices=CIRCUIT_TYPE_CHOICES, blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True, null=True)
    bandwidth = models.CharField(max_length=50, blank=True, null=True)
    customer_end_node = models.CharField(max_length=50, choices=NODE_CHOICES, blank=True, null=True)
    mc_type = models.CharField(max_length=100, blank=True, null=True)
    node_configuration = models.JSONField(blank=True, null=True)
    fiber_mode = models.CharField(max_length=10, choices=[('SINGLE', 'Single'), ('DUAL', 'Dual')], blank=True, null=True)
    cable = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True, blank=True)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.SET_NULL, null=True, blank=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True)
    customer_premise_location = models.CharField(max_length=255, blank=True, null=True)
    otdr_distance = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    lc_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="LC ID")
    a_media = models.CharField(max_length=100, blank=True, null=True, verbose_name="A-Media")
    a_address = models.TextField(blank=True, null=True, verbose_name="A-Address")
    node_at_a_end = models.CharField(max_length=100, blank=True, null=True, verbose_name="Node at A-End")
    node_at_b_end = models.CharField(max_length=100, blank=True, null=True, verbose_name="Node at B-End")
    port_b_side = models.CharField(max_length=100, blank=True, null=True, verbose_name="Port - B Side")
    status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Status")
    working_status = models.CharField(max_length=100, blank=True, null=True, verbose_name="Working Status")
    cable_data = models.CharField(max_length=255, blank=True, null=True, verbose_name="Cable Data")
    remarks = models.TextField()
    is_ring = models.BooleanField(default=False)
    ring_image = models.ImageField(
        upload_to='circuit_ring_images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
    )
    ring_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.client_name} - {self.circuit_type}"

class MobileBTS(models.Model):
    SITE_TYPE_CHOICES = [
        ('4G', '4G Site'),
        ('NON_4G', 'No 4G Site'),
    ]
    site_type = models.CharField(max_length=20, choices=SITE_TYPE_CHOICES, default='4G', verbose_name="Site Type")
    
    # Direct TE relationship (particularly useful for No 4G Sites)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.SET_NULL, null=True, blank=True, related_name='bts_sites', verbose_name="Telephone Exchange")
    
    rp_id = models.CharField(max_length=100, unique=True, verbose_name="RP ID")
    bts_name = models.CharField(max_length=255, verbose_name="BTS Name", default="Unnamed BTS")
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    place_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Non-4G Specific Fields
    NON_4G_TYPE_CHOICES = [
        ('2G', '2G'),
        ('3G', '3G'),
        ('5G', '5G'),
        ('2G_3G', '2G + 3G'),
        ('3G_5G', '3G + 5G'),
        ('2G_3G_5G', '2G + 3G + 5G'),
    ]
    non_4g_type = models.CharField(max_length=50, blank=True, null=True, choices=NON_4G_TYPE_CHOICES, verbose_name="No 4G Site Type")
    backhaul_media = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        choices=[('FIBER', 'Fiber'), ('MICROWAVE', 'Microwave'), ('LEASED_LINE', 'Leased Line')], 
        verbose_name="Backhaul Media"
    )
    connected_equipment = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        help_text="e.g. BSC, RNC, MSC, IP-BST", 
        verbose_name="Connected Node/Equipment"
    )
    
    has_cef_12t = models.BooleanField(default=False, verbose_name="Is CEF Having 12T")
    # CEF Ports data: list of dicts [{'port': 'P2', 'circuit': '', 'system_end': '', 'cable': ''}, ...]
    cef_ports_data = models.JSONField(default=dict, blank=True)
    
    is_ring = models.BooleanField(default=False, verbose_name="Is BTS in Ring")
    erps_image = models.ImageField(upload_to='bts_images/', blank=True, null=True, 
                                  validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])],
                                  help_text="Upload ERPS Connectivity Diagram (JPG only)")
    
    # Keeping old fields for compatibility if needed, but they seem redundant now
    maan_node = models.ForeignKey(Equipment, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'equipment_type__startswith': 'MAAN'})
    maan_port = models.CharField(max_length=50, blank=True, null=True)
    cable_name = models.CharField(max_length=100, blank=True, null=True)
    receive_power_db = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bts_name} ({self.rp_id})"

class JunctionBox(models.Model):
    JB_TYPE_CHOICES = [
        ('BAMBOO_BIG', 'Bamboo Big'),
        ('BAMBOO_SMALL', 'Bamboo Small'),
        ('SQUARE_BIG', 'Square Big'),
        ('SQUARE_SMALL', 'Square Small'),
    ]
    JB_CATEGORY_CHOICES = [
        ('UG', 'Underground'),
        ('OH', 'Overhead'),
    ]
    FIBER_TYPE_CHOICES = [
        ('288F', '288F'),
        ('96F', '96F'),
        ('48F', '48F'),
        ('24F', '24F'),
        ('12F', '12F'),
        ('6F', '6F'),
        ('4F', '4F'),
    ]
    
    jb_id = models.CharField(max_length=100, unique=True)
    jb_name = models.CharField(max_length=255, blank=True, null=True, help_text="Friendly name for the Junction Box")
    te = models.ForeignKey(TelephoneExchange, on_delete=models.CASCADE, related_name='junction_boxes', null=True, blank=True)
    cable_mode = models.CharField(max_length=2, choices=JB_CATEGORY_CHOICES)
    jb_type = models.CharField(max_length=20, choices=JB_TYPE_CHOICES)
    fiber_entering = models.CharField(max_length=255, blank=True, null=True, help_text="Fiber types entering JB (comma-separated)")
    fiber_out = models.CharField(max_length=255, blank=True, null=True, help_text="Fiber types leaving JB (comma-separated)")
    splicing_info = models.TextField(blank=True, null=True, help_text="Splicing information (e.g., 96F → 48F + 48F split)")
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    landmark = models.TextField(blank=True, null=True)
    jb_image = models.FileField(upload_to='jb_uploads/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])])
    input_cables = models.ManyToManyField(Cable, related_name='jb_inputs', blank=True)
    output_cables = models.ManyToManyField(Cable, related_name='jb_outputs', blank=True)
    remarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"JB {self.jb_id} ({self.get_cable_mode_display()})"

class FTTH(models.Model):
    customer_name = models.CharField(max_length=255)
    landline_number = models.CharField(max_length=20, unique=True)
    optical_power = models.DecimalField(max_digits=5, decimal_places=2, help_text="Format: -XX.XX dB")
    olt_name = models.CharField(max_length=255)
    port_number = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 9)])
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    division = models.ForeignKey(NWO, on_delete=models.SET_NULL, null=True, blank=True)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_name} - {self.landline_number}"

    class Meta:
        verbose_name = "FTTH Record"
        verbose_name_plural = "FTTH Records"
        ordering = ['-created_at']

class LIU(models.Model):
    CAPACITY_CHOICES = [
        (12, '12'),
        (24, '24'),
        (48, '48'),
        (96, '96'),
    ]
    name = models.CharField(max_length=100, default="Main LIU")
    te = models.ForeignKey(TelephoneExchange, on_delete=models.CASCADE)
    cable = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True, blank=True)
    cable_manual_entry = models.CharField(max_length=255, blank=True, null=True, help_text="Manual cable reference when dropdown selection not used")
    capacity = models.PositiveIntegerField(choices=CAPACITY_CHOICES)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    remarks = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.te.name})"

class LIUPort(models.Model):
    liu = models.ForeignKey(LIU, on_delete=models.CASCADE, related_name='ports')
    port_number = models.PositiveIntegerField()
    fiber = models.ForeignKey(Fiber, on_delete=models.SET_NULL, null=True, blank=True)
    connected_to = models.CharField(max_length=255, blank=True, null=True) # Equipment/Port
    status = models.CharField(max_length=50, default='Available')
    remarks = models.TextField(blank=True, null=True)
    otdr_distance = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 2.5 km")
    otdr_image = models.FileField(
        upload_to='liu_otdr_images/', 
        null=True, 
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'pdf'])]
    )

    class Meta:
        unique_together = ('liu', 'port_number')
        ordering = ['port_number']

    def __str__(self):
        return f"{self.liu} - Port {self.port_number}"

@receiver(post_save, sender=LIU)
def create_liu_ports(sender, instance, created, **kwargs):
    if created:
        ports = [LIUPort(liu=instance, port_number=i+1) for i in range(instance.capacity)]
        LIUPort.objects.bulk_create(ports)

class Splicing(models.Model):
    jb = models.ForeignKey(JunctionBox, on_delete=models.CASCADE, related_name='splices')
    fiber_in = models.ForeignKey(Fiber, on_delete=models.CASCADE, related_name='spliced_in')
    fiber_out = models.ForeignKey(Fiber, on_delete=models.CASCADE, related_name='spliced_out')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        unique_together = ('fiber_in', 'fiber_out')
        verbose_name_plural = "Splicing Records"
        ordering = ['-created_at']

    def __str__(self):
        return f"Splice: {self.fiber_in} <-> {self.fiber_out} in {self.jb}"

class CableRoutePoint(models.Model):
    cable = models.ForeignKey(Cable, on_delete=models.CASCADE, related_name='route_points')
    latitude = models.DecimalField(max_digits=12, decimal_places=9)
    longitude = models.DecimalField(max_digits=12, decimal_places=9)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ('cable', 'order')

    def __str__(self):
        return f"{self.cable.name} - Point {self.order}"

class OHMaintenanceRateMaster(models.Model):
    ACTIVITY_CHOICES = [
        ('OFC Cable Splicing', 'OFC Cable Splicing'),
        ('Re-shackling / Tightening of Sagged Cable', 'Re-shackling / Tightening of Sagged Cable'),
        ('Assembling and Erection of Cable Post', 'Assembling and Erection of Cable Post'),
        ('Erection of Aerial OFC up to 12F', 'Erection of Aerial OFC up to 12F'),
        ('Dismantling and Recovery of Unused Cables', 'Dismantling and Recovery of Unused Cables'),
        ('BSNL Name Tagging on OH Cables', 'BSNL Name Tagging on OH Cables'),
    ]
    UNIT_CHOICES = [
        ('Per Splice', 'Per Splice'),
        ('Per Span', 'Per Span'),
        ('Per Post', 'Per Post'),
        ('Per Meter', 'Per Meter'),
        ('Per Tag', 'Per Tag'),
    ]
    activity_type = models.CharField(max_length=100, choices=ACTIVITY_CHOICES)
    unit_type = models.CharField(max_length=50, choices=UNIT_CHOICES)
    unit_rate = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "OH Maintenance Rate Master"
        verbose_name_plural = "OH Maintenance Rate Masters"

    def __str__(self):
        return f"{self.activity_type} - {self.unit_rate} ({self.unit_type})"

class OHMaintenanceEntry(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Verified', 'Verified'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    division = models.ForeignKey(NWO, on_delete=models.CASCADE)
    te = models.ForeignKey(TelephoneExchange, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    team_name = models.CharField(max_length=255)
    work_order_no = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255)
    route_name = models.CharField(max_length=255, blank=True, null=True)
    pole_span_details = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    
    # Fault Tracking Fields
    FAULT_TYPE_CHOICES = [
        ('Cable Cut', 'Cable Cut'),
        ('Sagging Cable', 'Sagging Cable'),
        ('Pole Damage', 'Pole Damage'),
        ('Loose Shackling', 'Loose Shackling'),
        ('Fiber Break', 'Fiber Break'),
        ('Cable Theft', 'Cable Theft'),
        ('Wind / Rain Damage', 'Wind / Rain Damage'),
        ('Vehicle Hit Damage', 'Vehicle Hit Damage'),
        ('Joint Failure', 'Joint Failure'),
        ('Others', 'Others'),
    ]
    FAULT_SEVERITY_CHOICES = [
        ('Minor', 'Minor'),
        ('Medium', 'Medium'),
        ('Major', 'Major'),
        ('Critical', 'Critical'),
    ]
    fault_ticket_no = models.CharField(max_length=100, blank=True, null=True)
    fault_type = models.CharField(max_length=50, choices=FAULT_TYPE_CHOICES, blank=True, null=True)
    fault_occurrence_datetime = models.DateTimeField(blank=True, null=True)
    fault_clearance_datetime = models.DateTimeField(blank=True, null=True)
    fault_duration = models.CharField(max_length=100, blank=True, null=True)
    fault_severity = models.CharField(max_length=20, choices=FAULT_SEVERITY_CHOICES, blank=True, null=True)
    fault_cause = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='oh_entries_created')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='oh_entries_modified')
    modified_date = models.DateTimeField(auto_now=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='oh_entries_verified')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='oh_entries_approved')

    class Meta:
        verbose_name = "OH Maintenance Entry"
        verbose_name_plural = "OH Maintenance Entries"
        ordering = ['-maintenance_date', '-created_date']

    def __str__(self):
        return f"{self.maintenance_date} - {self.team_name} ({self.division.name})"

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        # Fault occurrence fields mandatory before submission
        if self.status in ['Submitted', 'Verified', 'Approved']:
            if not self.fault_occurrence_datetime:
                raise ValidationError({
                    'fault_occurrence_datetime': "Fault occurrence date and time are mandatory before submission."
                })
        
        # Fault clearance fields mandatory before approval
        if self.status == 'Approved':
            if not self.fault_clearance_datetime:
                raise ValidationError({
                    'fault_clearance_datetime': "Fault clearance date and time are mandatory before approval."
                })

        # Validation Rules
        if self.fault_occurrence_datetime and self.fault_clearance_datetime:
            if self.fault_clearance_datetime < self.fault_occurrence_datetime:
                raise ValidationError({
                    'fault_clearance_datetime': "Fault Clearance Date & Time cannot be earlier than Fault Occurrence Date & Time"
                })
            
            # Future date/time not allowed
            now = timezone.now()
            if self.fault_occurrence_datetime > now:
                raise ValidationError({
                    'fault_occurrence_datetime': "Future date/time not allowed"
                })
            if self.fault_clearance_datetime > now:
                raise ValidationError({
                    'fault_clearance_datetime': "Future date/time not allowed"
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class OHMaintenanceActivity(models.Model):
    entry = models.ForeignKey(OHMaintenanceEntry, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=100) # Copy from Rate Master
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_type = models.CharField(max_length=50)
    unit_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "OH Maintenance Activity"
        verbose_name_plural = "OH Maintenance Activities"

    def __str__(self):
        return f"{self.activity_type} - Qty: {self.quantity}"
