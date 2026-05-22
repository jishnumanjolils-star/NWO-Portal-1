import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nwo_portal.settings')
django.setup()

from inventory.models import NWO, TelephoneExchange

data = {
    'CENTRAL': [
        'Panambilly Nagar', 'CSR', 'BoatJetty', 'SRM', 'Mulavukad', 'Vaduthala', 
        'Chittoor', 'Vypin', 'Vyttila', 'Gandhi Nagar', 'Kaloor', 'Ayyappankavu'
    ],
    'PALARIVATTOM': [
        'Palarivattom', 'Thrikkakara', 'Vennala', 'Kalamassery', 'CUSAT', 'Edappally', 
        'Kangarappady', 'Kinfra', 'CSEZ', 'Eloor', 'Vyttila', 'BoatJetty', 'SRM', 'Gandhi Nagar'
    ],
    'KOCHI': [
        'Wellington Island', 'Palluruthy', 'Mattanchery', 'Fort kochi', 'Kumbalangy', 
        'Edakochi', 'Chellanam', 'Kandakkadavu', 'Thevara', 'Ravipuram', 'Nettoor', 
        'BoatJetty', 'Panambilly Nagar'
    ],
    'TRIPUNITHARA': [
        'Trippunithura', 'Maradu', 'Ambalamukal', 'Mulanthuruthy', 'Keechery', 
        'Arakkunnam', 'Chottanikkara', 'Thiruvankulam', 'Udayamperoor', 'Vyttila'
    ]
}

# Normalize names (strip numbers/dots if any, though the list above looks clean)
def normalize(name):
    return name.strip()

for nwo_code, exchanges in data.items():
    nwo_obj, _ = NWO.objects.get_or_create(name=nwo_code)
    print(f"NWO: {nwo_code}")
    
    for te_name in exchanges:
        name = normalize(te_name)
        te_obj, created = TelephoneExchange.objects.get_or_create(nwo=nwo_obj, name=name)
        if created:
            print(f"  Created TE: {name}")
        else:
            print(f"  TE: {name} already exists")

print("Population complete.")
