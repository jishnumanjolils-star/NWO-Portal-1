from django import forms
from .models import LIU, Cable, TelephoneExchange, JunctionBox, EBCircuit, Equipment, MobileBTS, FTTH, OHMaintenanceEntry, OHMaintenanceActivity, OHMaintenanceRateMaster

class DivisionFilteredFormMixin:
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_superuser:
            if hasattr(self.user, 'profile') and self.user.profile.division:
                division = self.user.profile.division
                if 'te' in self.fields:
                    self.fields['te'].queryset = TelephoneExchange.objects.filter(nwo=division)
                if 'connected_te' in self.fields:
                    self.fields['connected_te'].queryset = TelephoneExchange.objects.filter(nwo=division)
                if 'input_cables' in self.fields:
                    self.fields['input_cables'].queryset = Cable.objects.filter(te__nwo=division)
                if 'output_cables' in self.fields:
                    self.fields['output_cables'].queryset = Cable.objects.filter(te__nwo=division)
                if 'cable' in self.fields:
                    self.fields['cable'].queryset = Cable.objects.filter(te__nwo=division)
                if 'maan_node' in self.fields:
                    self.fields['maan_node'].queryset = Equipment.objects.filter(te__nwo=division, equipment_type__startswith='MAAN')
                if 'equipment' in self.fields:
                    self.fields['equipment'].queryset = Equipment.objects.filter(te__nwo=division)

class LIUForm(DivisionFilteredFormMixin, forms.ModelForm):
    class Meta:
        model = LIU
        fields = ['name', 'te', 'cable', 'cable_manual_entry', 'capacity', 'remarks', 'latitude', 'longitude']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 2}),
            'cable_manual_entry': forms.TextInput(attrs={'placeholder': 'Enter cable name manually if not in dropdown'}),
        }
        labels = {
            'te': 'TE Name',
            'cable_manual_entry': 'Manual Cable Entry',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True

class FTTHForm(DivisionFilteredFormMixin, forms.ModelForm):
    optical_power_display = forms.CharField(
        label="Optical Power",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., -23.45 dB', 'class': 'form-control'}),
        help_text="Must be a negative value. Format: -XX.XX dB"
    )

    class Meta:
        model = FTTH
        fields = ['customer_name', 'landline_number', 'olt_name', 'port_number', 'latitude', 'longitude', 'division', 'te']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Customer Name'}),
            'landline_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Landline FTTH Number'}),
            'olt_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'OLT Name'}),
            'port_number': forms.Select(attrs={'class': 'form-select'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Latitude', 'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Longitude', 'class': 'form-control'}),
            'division': forms.Select(attrs={'class': 'form-select'}),
            'te': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'te': 'TE Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.optical_power:
            self.fields['optical_power_display'].initial = f"{self.instance.optical_power} dB"
        
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True
        if 'division' in self.initial or (self.instance and self.instance.division_id):
            self.fields['division'].disabled = True

    def clean_optical_power_display(self):
        val_str = self.cleaned_data.get('optical_power_display')
        if not val_str:
            raise forms.ValidationError("Optical Power is required.")
        
        # Extract number using regex
        import re
        match = re.search(r'(-?[\d.]+)', val_str)
        if not match:
            raise forms.ValidationError("Invalid format. Use e.g., -23.45 dB")
        
        try:
            val = float(match.group(1))
            if val >= 0:
                raise forms.ValidationError("Optical Power must be a negative value.")
            return val
        except ValueError:
            raise forms.ValidationError("Invalid numerical value.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.optical_power = self.cleaned_data.get('optical_power_display')
        if commit:
            instance.save()
        return instance

class JBForm(DivisionFilteredFormMixin, forms.ModelForm):
    # Multi-select for fiber types
    fiber_entering = forms.MultipleChoiceField(
        choices=JunctionBox.FIBER_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Fiber Entering Details',
        help_text='Select fiber types entering the Junction Box'
    )
    fiber_out = forms.MultipleChoiceField(
        choices=JunctionBox.FIBER_TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Fiber Out Details',
        help_text='Select fiber types leaving the Junction Box'
    )

    class Meta:
        model = JunctionBox
        fields = ['jb_id', 'jb_name', 'te', 'cable_mode', 'jb_type', 'fiber_entering', 'fiber_out', 
                  'splicing_info', 'landmark', 'latitude', 'longitude', 'remarks', 'input_cables', 'output_cables', 'jb_image']
        widgets = {
            'jb_id': forms.TextInput(attrs={
                'placeholder': 'e.g., TE-JB-001',
                'class': 'form-control'
            }),
            'jb_name': forms.TextInput(attrs={
                'placeholder': 'Friendly name for this Junction Box',
                'class': 'form-control'
            }),
            'cable_mode': forms.Select(attrs={'class': 'form-select'}),
            'jb_type': forms.Select(attrs={'class': 'form-select'}),
            'splicing_info': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g., 96F → 48F + 48F split',
                'class': 'form-control'
            }),
            'landmark': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'JB Landmark/Description',
                'class': 'form-control'
            }),
            'latitude': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'GPS Latitude',
                'class': 'form-control'
            }),
            'longitude': forms.NumberInput(attrs={
                'step': 'any',
                'placeholder': 'GPS Longitude',
                'class': 'form-control'
            }),
            'remarks': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Additional remarks',
                'class': 'form-control'
            }),
            'input_cables': forms.CheckboxSelectMultiple,
            'output_cables': forms.CheckboxSelectMultiple,
            'jb_image': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg,.pdf,application/pdf,image/jpeg'}),
        }
        labels = {
            'te': 'TE Name (Main Module)',
            'jb_id': 'Junction Box ID',
            'jb_name': 'Junction Box Name',
            'cable_mode': 'JB Category',
            'jb_type': 'JB Type',
            'splicing_info': 'Splicing Information',
            'input_cables': 'Input Cables',
            'output_cables': 'Output Cables',
            'jb_image': 'JB Image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['te'].queryset = TelephoneExchange.objects.all()
        self.fields['input_cables'].queryset = Cable.objects.all()
        self.fields['output_cables'].queryset = Cable.objects.all()
        
        # Auto-fill and disable TE field if provided
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True
            # Set read-only display
            if self.instance and self.instance.te_id:
                self.fields['te'].widget.attrs['readonly'] = True
        
        # Convert comma-separated strings to lists for multi-select
        if self.instance and self.instance.pk:
            if self.instance.fiber_entering:
                self.fields['fiber_entering'].initial = [f.strip() for f in self.instance.fiber_entering.split(',')]
            if self.instance.fiber_out:
                self.fields['fiber_out'].initial = [f.strip() for f in self.instance.fiber_out.split(',')]

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert list of fiber types to comma-separated string
        instance.fiber_entering = ', '.join(self.cleaned_data.get('fiber_entering', []))
        instance.fiber_out = ', '.join(self.cleaned_data.get('fiber_out', []))
        if commit:
            instance.save()
        return instance


class CableForm(DivisionFilteredFormMixin, forms.ModelForm):
    otdr_distance_display = forms.CharField(
        required=False,
        label="OTDR Distance (in meters/km)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g., 2.35 km', 'class': 'form-control'})
    )

    class Meta:
        model = Cable
        fields = '__all__'
        exclude = ['otdr_distance']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'TRANSNET CABLE NAME'}),
            'transnet_id': forms.TextInput(attrs={'placeholder': 'TRANSNET ID'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Mandatory - Enter details'}),
            'te': forms.Select(attrs={'class': 'form-select'}),
            'connected_te': forms.Select(attrs={'class': 'form-select'}),
            'otdr_image': forms.FileInput(attrs={'class': 'form-control', 'accept': '.jpg,.jpeg'}),
        }
        labels = {
            'name': 'TRANSNET CABLE NAME',
            'transnet_id': 'TRANSNET ID',
            'te': 'TE Name',
            'connected_te': 'Connected TE Name',
            'otdr_image': 'OTDR Image',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['te'].queryset = TelephoneExchange.objects.all()
        self.fields['connected_te'].queryset = TelephoneExchange.objects.all()
        
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True

        if self.instance and self.instance.otdr_distance is not None:
            m = self.instance.otdr_distance
            if m >= 1000:
                self.fields['otdr_distance_display'].initial = f"{m/1000:g} km"
            else:
                self.fields['otdr_distance_display'].initial = f"{m:g} m"

    def clean_otdr_distance_display(self):
        val_str = self.cleaned_data.get('otdr_distance_display')
        if not val_str:
            return None
        import re
        match = re.search(r'([\d.]+)', val_str)
        if match:
            try:
                val = float(match.group(1))
                if 'km' in val_str.lower():
                    return val * 1000
                elif 'm' in val_str.lower():
                    return val
                else:
                    return val
            except ValueError:
                raise forms.ValidationError("Invalid format. Use e.g., '2.35 km' or '2350 m'")
        return None

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.otdr_distance = self.cleaned_data.get('otdr_distance_display')
        if commit:
            instance.save()
        return instance

class EquipmentForm(DivisionFilteredFormMixin, forms.ModelForm):
    configuration_json = forms.CharField(widget=forms.HiddenInput(), required=False)
    free_ports = forms.IntegerField(required=False, disabled=True, label="Free Ports")

    class Meta:
        model = Equipment
        fields = '__all__'
        exclude = ['configuration']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Equipment Name'}),
            'uplink_connectivity': forms.TextInput(attrs={'placeholder': 'Uplink Connection Details'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Mandatory - Enter details'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'GPS Latitude'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'GPS Longitude'}),
        }
        labels = {
            'te': 'TE Name',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['te'].queryset = TelephoneExchange.objects.all()
        
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True

        if self.instance and self.instance.configuration:
            import json
            self.fields['configuration_json'].initial = json.dumps(self.instance.configuration)

        total_ports = getattr(self.instance, 'total_ports', None)
        used_ports = getattr(self.instance, 'used_ports', 0) or 0
        if total_ports is not None:
            self.fields['free_ports'].initial = max(int(total_ports) - int(used_ports), 0)

    def save(self, commit=True):
        instance = super().save(commit=False)
        config_data = self.cleaned_data.get('configuration_json')
        if config_data:
            import json
            try:
                instance.configuration = json.loads(config_data)
            except json.JSONDecodeError:
                pass
        if commit:
            instance.save()
        return instance

class CircuitForm(DivisionFilteredFormMixin, forms.ModelForm):
    circuit_type_multi = forms.ChoiceField(
        choices=[('', '---------')] + EBCircuit.CIRCUIT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        label="Circuit Type"
    )

    node_configuration_json = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = EBCircuit
        fields = '__all__'
        exclude = ['circuit_type', 'node_configuration']
        widgets = {
            'client_name': forms.TextInput(attrs={'placeholder': 'Client Name'}),
            'bandwidth': forms.TextInput(attrs={'placeholder': 'Bandwidth (e.g., 100 Mbps)'}),
            'customer_end_node': forms.Select(attrs={'class': 'form-select'}),
            'mc_type': forms.TextInput(attrs={'placeholder': 'Type of Media Converter'}),
            'customer_premise_location': forms.TextInput(attrs={'placeholder': 'Customer Premise Location'}),
            'otdr_distance': forms.TextInput(attrs={'placeholder': 'OTDR Distance (e.g., 2.5 km)'}),
            'lc_id': forms.TextInput(attrs={'placeholder': 'Leased Circuit ID'}),
            'a_media': forms.TextInput(attrs={'placeholder': 'e.g. Media Converter / Fiber'}),
            'a_address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Address at Client End'}),
            'node_at_a_end': forms.TextInput(attrs={'placeholder': 'Node details at A-End'}),
            'node_at_b_end': forms.TextInput(attrs={'placeholder': 'Node details at B-End'}),
            'port_b_side': forms.TextInput(attrs={'placeholder': 'Port at B-End'}),
            'status': forms.TextInput(attrs={'placeholder': 'e.g. Working / Idle'}),
            'working_status': forms.TextInput(attrs={'placeholder': 'e.g. Active / Testing'}),
            'cable_data': forms.TextInput(attrs={'placeholder': 'Associated Cable Data'}),
            'remarks': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Mandatory - Enter details'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'GPS Latitude'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'GPS Longitude'}),
            'is_ring': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'ring_image': forms.ClearableFileInput(attrs={'accept': '.jpg,.jpeg,image/jpeg'}),
            'ring_summary': forms.Textarea(attrs={'rows': 4, 'maxlength': 1000, 'placeholder': 'Ring Summary (mandatory if Circuit in Ring = Yes)'}),
        }
        labels = {
            'te': 'TE Name',
            'lc_id': 'LC ID',
            'a_media': 'A-Media',
            'a_address': 'A-Address',
            'node_at_a_end': 'Node at A-End',
            'node_at_b_end': 'Node at B-End',
            'port_b_side': 'Port - B Side',
            'status': 'Status',
            'working_status': 'Working Status',
            'cable_data': 'Cable Data',
            'is_ring': 'Circuit in Ring?',
            'ring_image': 'Ring Details Upload',
            'ring_summary': 'Ring Summary',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['te'].queryset = TelephoneExchange.objects.all()
        self.fields['cable'].queryset = Cable.objects.all()
        self.fields['equipment'].queryset = Equipment.objects.all()
        
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True
        
        if self.instance and self.instance.circuit_type:
            self.fields['circuit_type_multi'].initial = self.instance.circuit_type
        
        if self.instance and self.instance.node_configuration:
            import json
            self.fields['node_configuration_json'].initial = json.dumps(self.instance.node_configuration)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.circuit_type = self.cleaned_data['circuit_type_multi']
        
        config_data = self.cleaned_data.get('node_configuration_json')
        if config_data:
            import json
            try:
                instance.node_configuration = json.loads(config_data)
            except json.JSONDecodeError:
                pass
        
        if commit:
            instance.save()
        return instance

    def clean_ring_image(self):
        img = self.cleaned_data.get('ring_image')
        if not img:
            return img
        if getattr(img, 'size', 0) > 5 * 1024 * 1024:
            raise forms.ValidationError('Ring image must be 5 MB or smaller.')
        return img

    def clean(self):
        cleaned = super().clean()
        bw = cleaned.get('bandwidth') or ''
        is_ring = cleaned.get('is_ring')
        summary = (cleaned.get('ring_summary') or '').strip()

        def parse_to_mbps(val):
            import re
            s = str(val).strip().lower()
            if not s:
                return None
            m = re.search(r'(\d+(?:\.\d+)?)\s*([a-z]+)?', s)
            if not m:
                return None
            num = float(m.group(1))
            unit = (m.group(2) or 'mbps').lower()
            if unit in ('g', 'gb', 'gbps'):
                return num * 1000
            if unit in ('k', 'kb', 'kbps'):
                return num / 1000
            if unit in ('m', 'mb', 'mbps'):
                return num
            return num

        bw_mbps = parse_to_mbps(bw)
        if bw_mbps is not None and bw_mbps > 10 and is_ring is True:
            if not summary:
                self.add_error('ring_summary', 'Ring Summary is mandatory when Bandwidth > 10 Mbps and Circuit in Ring is Yes.')

        return cleaned

class BTSForm(DivisionFilteredFormMixin, forms.ModelForm):
    # Additional fields for CEF Ports (will be handled in clean/save)
    # We use CharFields but they will be rendered as a group in the template
    p2_circuit = forms.CharField(required=False, label="P2 Circuit Name")
    p2_system_end = forms.CharField(required=False, label="P2 System End")
    p2_cable = forms.CharField(required=False, label="P2 Cable Name")
    
    p3_circuit = forms.CharField(required=False, label="P3 Circuit Name")
    p3_system_end = forms.CharField(required=False, label="P3 System End")
    p3_cable = forms.CharField(required=False, label="P3 Cable Name")
    
    p4_circuit = forms.CharField(required=False, label="P4 Circuit Name")
    p4_system_end = forms.CharField(required=False, label="P4 System End")
    p4_cable = forms.CharField(required=False, label="P4 Cable Name")
    
    p5_circuit = forms.CharField(required=False, label="P5 Circuit Name")
    p5_system_end = forms.CharField(required=False, label="P5 System End")
    p5_cable = forms.CharField(required=False, label="P5 Cable Name")

    class Meta:
        model = MobileBTS
        fields = [
            'rp_id', 'bts_name', 'latitude', 'longitude', 'place_name',
            'has_cef_12t', 'is_ring', 'erps_image'
        ]
        widgets = {
            'has_cef_12t': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'is_ring': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'id': 'id_latitude', 'placeholder': 'Auto-captured or manual'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'id': 'id_longitude', 'placeholder': 'Auto-captured or manual'}),
            'bts_name': forms.TextInput(attrs={'placeholder': 'Enter BTS Name'}),
            'rp_id': forms.TextInput(attrs={'placeholder': 'Enter RP ID'}),
            'place_name': forms.TextInput(attrs={'placeholder': 'Optional Place Name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate extra fields if instance exists
        if self.instance and self.instance.cef_ports_data:
            data = self.instance.cef_ports_data
            for port in ['p2', 'p3', 'p4', 'p5']:
                if port in data:
                    self.fields[f'{port}_circuit'].initial = data[port].get('circuit', '')
                    self.fields[f'{port}_system_end'].initial = data[port].get('system_end', '')
                    self.fields[f'{port}_cable'].initial = data[port].get('cable', '')

    def clean(self):
        cleaned_data = super().clean()
        has_cef_12t = cleaned_data.get('has_cef_12t')
        
        # P2 is always required if we have CEF (as per user instruction: "If NO (N): Enable: Only P2")
        # However, user says "Enable: Only P2" - implying it becomes accessible. 
        # I will keep them optional in CharField but the logic will handle them.
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Consolidate port data into JSON
        ports_data = {}
        for port in ['p2', 'p3', 'p4', 'p5']:
            ports_data[port] = {
                'circuit': self.cleaned_data.get(f'{port}_circuit', ''),
                'system_end': self.cleaned_data.get(f'{port}_system_end', ''),
                'cable': self.cleaned_data.get(f'{port}_cable', ''),
            }
        instance.cef_ports_data = ports_data
        if commit:
            instance.save()
        return instance


class Non4GBTSForm(DivisionFilteredFormMixin, forms.ModelForm):
    class Meta:
        model = MobileBTS
        fields = [
            'rp_id', 'bts_name', 'te', 'latitude', 'longitude', 'place_name',
            'non_4g_type', 'backhaul_media', 'connected_equipment', 'remarks'
        ]
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Latitude'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Longitude'}),
            'bts_name': forms.TextInput(attrs={'placeholder': 'Enter Site Name'}),
            'rp_id': forms.TextInput(attrs={'placeholder': 'Enter RP ID / Site ID'}),
            'place_name': forms.TextInput(attrs={'placeholder': 'Optional Place Name'}),
            'connected_equipment': forms.TextInput(attrs={'placeholder': 'e.g. BSC, RNC, MSC, IP-BST'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional remarks...'}),
        }
        labels = {
            'te': 'Telephone Exchange',
            'non_4g_type': 'No 4G Site Type',
            'backhaul_media': 'Backhaul Media',
            'connected_equipment': 'Connected Node/Equipment',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['te'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.site_type = 'NON_4G'
        if commit:
            instance.save()
        return instance


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        val = self.cleaned_data.get('current_password') or ''
        if not self.user or not self.user.check_password(val):
            raise forms.ValidationError('Current password incorrect')
        return val

    def clean_new_password(self):
        import re

        val = self.cleaned_data.get('new_password') or ''
        errors = []
        if len(val) < 8:
            errors.append('Minimum 8 characters')
        if not re.search(r'[A-Z]', val):
            errors.append('At least 1 uppercase letter')
        if not re.search(r'[a-z]', val):
            errors.append('At least 1 lowercase letter')
        if not re.search(r'\d', val):
            errors.append('At least 1 number')
        if not re.search(r'[^A-Za-z0-9]', val):
            errors.append('At least 1 special character')
        if errors:
            raise forms.ValidationError('Password does not meet criteria')
        return val

    def clean(self):
        cleaned = super().clean()
        new_password = cleaned.get('new_password')
        confirm = cleaned.get('confirm_new_password')
        if new_password and confirm and new_password != confirm:
            raise forms.ValidationError('New passwords do not match')
        return cleaned

class OHMaintenanceEntryForm(DivisionFilteredFormMixin, forms.ModelForm):
    # Split DateTime fields for better UI as requested
    fault_occurrence_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fault_occurrence_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    fault_clearance_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    fault_clearance_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )

    class Meta:
        model = OHMaintenanceEntry
        fields = [
            'maintenance_date', 'team_name', 'work_order_no', 
            'location', 'route_name', 'pole_span_details', 'remarks', 'te',
            'fault_ticket_no', 'fault_type', 'fault_severity', 'fault_cause', 'fault_duration'
        ]
        labels = {
            'te': 'TE Name',
        }
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'team_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Maintenance Team Name'}),
            'work_order_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'WO / Fault Ticket No'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location / Area'}),
            'route_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Route Name / Cable Route'}),
            'pole_span_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pole ID / Span Details'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
            'te': forms.Select(attrs={'class': 'form-select'}),
            'fault_ticket_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fault Ticket Number'}),
            'fault_type': forms.Select(attrs={'class': 'form-select'}),
            'fault_severity': forms.Select(attrs={'class': 'form-select'}),
            'fault_cause': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Reason for fault'}),
            'fault_duration': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'te' in self.initial or (self.instance and self.instance.te_id):
            self.fields['te'].disabled = True
        
        # Initialize split fields from instance
        if self.instance and self.instance.fault_occurrence_datetime:
            self.fields['fault_occurrence_date'].initial = self.instance.fault_occurrence_datetime.date()
            self.fields['fault_occurrence_time'].initial = self.instance.fault_occurrence_datetime.time()
        
        if self.instance and self.instance.fault_clearance_datetime:
            self.fields['fault_clearance_date'].initial = self.instance.fault_clearance_datetime.date()
            self.fields['fault_clearance_time'].initial = self.instance.fault_clearance_datetime.time()

    def clean(self):
        cleaned_data = super().clean()
        
        # Combine Date and Time for Occurrence
        occ_date = cleaned_data.get('fault_occurrence_date')
        occ_time = cleaned_data.get('fault_occurrence_time')
        if occ_date and occ_time:
            from django.utils import timezone
            import datetime
            dt = datetime.datetime.combine(occ_date, occ_time)
            cleaned_data['fault_occurrence_datetime'] = timezone.make_aware(dt)
        
        # Combine Date and Time for Clearance
        clr_date = cleaned_data.get('fault_clearance_date')
        clr_time = cleaned_data.get('fault_clearance_time')
        if clr_date and clr_time:
            from django.utils import timezone
            import datetime
            dt = datetime.datetime.combine(clr_date, clr_time)
            cleaned_data['fault_clearance_datetime'] = timezone.make_aware(dt)

        # Validation Rules
        occ_dt = cleaned_data.get('fault_occurrence_datetime')
        clr_dt = cleaned_data.get('fault_clearance_datetime')
        
        if occ_dt and clr_dt:
            if clr_dt < occ_dt:
                self.add_error('fault_clearance_date', "Fault Clearance Date & Time cannot be earlier than Fault Occurrence Date & Time")
            
            # Future date/time not allowed
            from django.utils import timezone
            now = timezone.now()
            if occ_dt > now:
                self.add_error('fault_occurrence_date', "Future date/time not allowed")
            if clr_dt > now:
                self.add_error('fault_clearance_date', "Future date/time not allowed")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fault_occurrence_datetime = self.cleaned_data.get('fault_occurrence_datetime')
        instance.fault_clearance_datetime = self.cleaned_data.get('fault_clearance_datetime')
        
        # Calculate duration if both are present
        if instance.fault_occurrence_datetime and instance.fault_clearance_datetime:
            diff = instance.fault_clearance_datetime - instance.fault_occurrence_datetime
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            parts = []
            if days > 0:
                parts.append(f"{days} Day{'s' if days > 1 else ''}")
            if hours > 0:
                parts.append(f"{hours} Hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                parts.append(f"{minutes} Minute{'s' if minutes > 1 else ''}")
            
            instance.fault_duration = " ".join(parts) if parts else "0 Minutes"
            
        if commit:
            instance.save()
        return instance

class OHMaintenanceActivityForm(forms.ModelForm):
    class Meta:
        model = OHMaintenanceActivity
        fields = ['activity_type', 'quantity', 'unit_type', 'unit_rate', 'amount', 'remarks']
        widgets = {
            'activity_type': forms.Select(attrs={'class': 'form-select activity-type-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': '0.01'}),
            'unit_type': forms.TextInput(attrs={'class': 'form-control unit-type-input', 'readonly': 'readonly'}),
            'unit_rate': forms.NumberInput(attrs={'class': 'form-control unit-rate-input', 'step': '0.01'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control amount-input', 'step': '0.01', 'readonly': 'readonly'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional remarks'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['activity_type'].widget.choices = [('', 'Select Activity')] + OHMaintenanceRateMaster.ACTIVITY_CHOICES

OHMaintenanceActivityFormSet = forms.inlineformset_factory(
    OHMaintenanceEntry, 
    OHMaintenanceActivity,
    form=OHMaintenanceActivityForm,
    extra=1,
    can_delete=True
)
