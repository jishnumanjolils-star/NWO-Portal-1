import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nwo_portal.settings')
django.setup()

from inventory.models import NWO, TelephoneExchange

# Exact data from user
data = {
    'CENTRAL': [
        'Panambilly Nagar TE', 'CSR TE', 'BoatJetty TE', 'SRM TE', 'Mulavukad TE', 'Vaduthala TE', 
        'Chittoor TE', 'Vypin TE', 'Vyttila TE', 'Gandhi Nagar TE', 'Kaloor TE', 'Ayyappankavu TE'
    ],
    'PALARIVATTOM': [
        'Palarivattom TE', 'Thrikkakara TE', 'Vennala TE', 'Kalamassery TE', 'CUSAT TE', 'Edappally TE', 
        'Kangarappady TE', 'Kinfra TE', 'CSEZ TE', 'Eloor TE', 'Vyttila TE', 'Boat Jetty TE', 'SRM TE', 'Gandhinagar TE'
    ],
    'KOCHI': [
        'Wellington Island TE', 'Palluruthy TE', 'Mattanchery TE', 'Fort kochi TE', 'Kumbalangy TE', 
        'Edakochi TE', 'Chellanam TE', 'Kandakkadavu TE', 'Thevara TE', 'Ravipuram TE', 'Nettoor TE', 
        'Boat Jetty TE', 'Panambillynagar TE'
    ],
    'TRIPUNITHARA': [
        'Trippunithura TE', 'Maradu TE', 'Ambalamukal TE', 'Mulanthuruthy TE', 'Keechery TE', 
        'Arakkunnam TE', 'Chottanikkara TE', 'Thiruvankulam TE', 'Udayamperoor TE', 'Vyttila TE'
    ]
}

# Delete old TEs to avoid confusion and re-populate
TelephoneExchange.objects.all().delete()

for code, exchanges in data.items():
    nwo_obj, _ = NWO.objects.get_or_create(name=code)
    print(f"Syncing NWO: {code}")
    for name in exchanges:
        TelephoneExchange.objects.get_or_create(nwo=nwo_obj, name=name)
        print(f"  Added: {name}")

print("Sync complete.")
