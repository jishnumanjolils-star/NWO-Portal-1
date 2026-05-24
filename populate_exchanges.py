#!/usr/bin/env python
"""
Script to populate telephone exchanges (TE) for each NWO division
Master TE List as provided
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nwo_portal.settings')
django.setup()

from inventory.models import NWO, TelephoneExchange

# Complete TE Master List for all divisions
DIVISIONS_EXCHANGES = {
    'NWO CENTRAL': [
        'Boatjetty TE',
        'Panampilly Nagar TE',
        'Csr TE',
        'Ayyappankavu TE',
        'Chittoor TE',
        'Vaduthala TE',
        'Kaloor TE',
        'Srm TE',
        'Gandhinagar TE',
        'Mulavukad TE',
    ],
    'NWO PALARIVATTOM': [
        'Palarivattom TE',
        'Thrikkakara TE',
        'Vennala TE',
        'Kalamassery TE',
        'Cusat TE',
        'Edappally TE',
        'Kangarappady TE',
        'Kinfra TE',
        'Csez TE',
        'Eloor TE',
    ],
    'NWO KOCHI': [
        'Wellington Island TE',
        'Palluruthy TE',
        'Mattanchery TE',
        'Fort Kochi TE',
        'Kumbalangy TE',
        'Edakochi TE',
        'Chellanam TE',
        'Kandakkadavu TE',
        'Thevara TE',
        'Ravipuram TE',
        'Nettoor TE',
    ],
    'NWO TRIPUNITHARA': [
        'Tripunithura TE',
        'Maradu TE',
        'Ambalamukal TE',
        'Mulanthuruthy TE',
        'Keechery TE',
        'Arakkunnam TE',
        'Chottanikkara TE',
        'Thiruvankulam TE',
        'Udayamperoor TE',
        'Vyttila TE',
    ],
    'NWO ANGAMALY': [
        'Anappara TE',
        'Angamali TE',
        'Angamali DET Off TE',
        'Ayyampuzha TE',
        'Kaladi TE',
        'Karukutty TE',
        'Malayatoor TE',
        'Manjapra TE',
        'Mookkanoor TE',
        'Nedumbassery TE',
        'Paduapuram TE',
        'Sreemoolanagarm TE',
        'Thuravoor TE',
        'Valayanchirangara TE',
        'Keezhillam TE',
        'Odakkaly TE',
        'Vengoor TE',
        'Kombanad TE',
        'Chundakkuzhy TE',
        'Koovappady TE',
        'Perumbavoor TE',
    ],
    'NWO THODUPUZHA': [
        'Thodupuzha TE',
        'Karimannoor TE',
        'Udumbannoor TE',
        'Vannappuram TE',
        'Kodikkulam TE',
        'Ezhalloor TE',
        'Parappuzha TE',
        'Kaloor TE',
        'Muttam TE',
        'Arakkulam TE',
        'Anchiri TE',
        'Kulamav TE',
        'Karimkunnam TE',
        'Vengalloor TE',
        'Arikkuzha TE',
    ],
    'NWO ALUVA': [
        'Aluva TE',
        'Thottakatukara TE',
        'Chengamanad TE',
        'Moozhikulam TE',
        'Pattimattom TE',
        'Marampilly TE',
        'Choondy TE',
        'Kizhakambalam TE',
        'Alangad TE',
        'Kunnukara TE',
        'North Parur TE',
        'Vypin TE',
        'Njarakal TE',
        'Edavanakad TE',
        'Cherai TE',
        'Chendamangalam TE',
        'Moothakunam TE',
        'Ezhikkara TE',
        'Varapuzha TE',
        'Puthenvelikkara TE',
    ],
    'NWO MOOVATTUPUZHA': [
        'Puthencruze TE',
        'Kolenchery TE',
        'Maneed TE',
        'Piravom TE',
        'Ramamangalam TE',
        'Ooramana TE',
        'Elanji TE',
        'Pampakkuda TE',
        'Koothattukulam TE',
        'Pandappilly TE',
        'Vazhappilly TE',
        'Muvattupuzha TE',
        'Vazhakkulam TE',
        'Perumattom TE',
        'Varappetty TE',
        'Pothanicad TE',
        'Kadavoor TE',
        'Kalloorkad TE',
        'Kothamangalam TE',
        'Kozhippilly TE',
        'Nellimattam TE',
        'Oonnukal TE',
        'Neriyamangalam TE',
        'Chelad TE',
        'Kuttampuzha TE',
        'Vadattupara TE',
        'Idamalayar TE',
        'Mekadamb TE',
        'Cheruvattoor TE',
        'Kottappady TE',
    ],
    'NWO ADIMALY': [
        'Adimali TE',
        'Munnar TE',
        'Irumbupalam TE',
        'Iruttukanam TE',
        'Chithirapuram TE',
        'Chithirapuram BTS TE',
        'Mankulam TE',
        'Bison Valley TE',
        'Devikulam TE',
        'Munnar Micro Wave TE',
        'Rajamala TE',
        'Thalayar TE',
        'Marayoor TE',
        'Kanthalloor TE',
        'Mattupatti TE',
        'Yellappetty TE',
        'Koviloor TE',
    ],
    'NWO KATTAPPANA': [
        'Idukki TE',
        'Kanjikuzhi TE',
        'Vazhathop TE',
        'Anakkara TE',
        'Chemmannar TE',
        'Erattayar TE',
        'Ezhukumvayal TE',
        'Kallar TE',
        'Kattappana TE',
        'Kochera TE',
        'Murikkassery TE',
        'Nedumkandam TE',
        'Parathodu TE',
        'Puliyanmala TE',
        'Rajakkad TE',
        'Rajakumary TE',
        'Santhanpara TE',
        'Senapathy TE',
        'Suryanelly TE',
        'Swaraj TE',
        'Thankamany TE',
        'Udumbanchola TE',
        'Vazhavara TE',
        'Anavilasom TE',
        'Cheruvallikulam TE',
        'Cumbummettu TE',
        'Elappara TE',
        'Kumily TE',
        'Mlamala TE',
        'Peermedu TE',
        'Peruvanthanam TE',
        'Kumily MW',
        'Kattappana MW',
        'Peermedu MW',
    ],
}

def populate_exchanges():
    print("Populating Telephone Exchanges (TE Master List)...")
    print("="*70)
    
    total_created = 0
    
    for division_name, exchanges in DIVISIONS_EXCHANGES.items():
        try:
            nwo = NWO.objects.get(name=division_name)
            print(f"\n{division_name}: ({len(exchanges)} TEs)")
            
            for exchange_name in exchanges:
                te, created = TelephoneExchange.objects.get_or_create(
                    nwo=nwo,
                    name=exchange_name,
                    defaults={'remarks': f'TE under {division_name}'}
                )
                
                if created:
                    total_created += 1
            
            print(f"  ✓ {len(exchanges)} TEs created/verified")
        
        except NWO.DoesNotExist:
            print(f"\n✗ Division not found: {division_name}")
    
    print("\n" + "="*70)
    print(f"Total TEs in database: {TelephoneExchange.objects.count()}")
    print(f"Total TEs just created: {total_created}")
    print("="*70)

if __name__ == '__main__':
    populate_exchanges()
    print("\n✓ All TEs populated successfully!")
