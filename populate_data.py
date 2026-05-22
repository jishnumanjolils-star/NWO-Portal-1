import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nwo_portal.settings')
django.setup()

from inventory.models import NWO, TelephoneExchange

def populate():
    nwos_data = {
        'CENTRAL': [
            'Panambilly Nagar', 'CSR', 'Boat Jetty', 'SRM', 'Mulavukad', 
            'Vaduthala', 'Chittoor', 'Vypin', 'Vyttila', 'Gandhi Nagar', 
            'Kaloor', 'Ayyappankavu'
        ],
        'PALARIVATTOM': [
            'Palarivattom', 'Thrikkakkara', 'Vennala', 'Kalamasery', 'Cusat', 
            'Edappally', 'Kangarapady', 'Kinfra', 'CSEZ', 'Eloor', 
            'Boat Jetty', 'Kaloor', 'Vyttila', 'SRM'
        ],
        'KOCHI': [
            'Wellington Island', 'Palluruthy', 'Mattanchery', 'Fort Kochi', 
            'Kumbalangy', 'Edakochi', 'Chellanam', 'Kandakkadavu', 
            'Thevara', 'Ravipuram', 'Nettoor', 'Boat Jetty', 'Panambilly Nagar'
        ],
        'TRIPUNITHARA': [
            'Tripunithara', 'Maradu', 'Ambalamugal', 'Mulanthuruthy', 
            'Keechery', 'Arakunnam', 'Chottanikkara', 'Thiruvankulam', 
            'Udayamperoor', 'Vyttila'
        ]
    }

    for nwo_code, te_list in nwos_data.items():
        nwo, created = NWO.objects.get_or_create(name=nwo_code)
        if created:
            print(f"Created NWO: {nwo_code}")
        
        for te_name in te_list:
            te, te_created = TelephoneExchange.objects.get_or_create(nwo=nwo, name=te_name)
            if te_created:
                print(f"  Created TE: {te_name}")

if __name__ == '__main__':
    populate()
