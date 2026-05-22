import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nwo_portal.settings')
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventory.models import Cable, Equipment, EBCircuit, MobileBTS, LIU, JunctionBox

def setup_roles():
    # Create Groups
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    field_engineer_group, _ = Group.objects.get_or_create(name='Field Engineer')
    viewer_group, _ = Group.objects.get_or_create(name='Viewer')

    # Permissions
    models = [Cable, Equipment, EBCircuit, MobileBTS, LIU, JunctionBox]
    
    for model in models:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        
        for perm in permissions:
            # Admin gets all
            admin_group.permissions.add(perm)
            
            # Field Engineer gets view, add, change (no delete)
            if perm.codename.startswith(('view_', 'add_', 'change_')):
                field_engineer_group.permissions.add(perm)
            
            # Viewer gets view only
            if perm.codename.startswith('view_'):
                viewer_group.permissions.add(perm)

    print("User roles and permissions set up successfully!")

if __name__ == '__main__':
    setup_roles()
