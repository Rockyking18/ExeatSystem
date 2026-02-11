import os
import django
import psycopg2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeat.settings')
django.setup()

from django.conf import settings
from django.db import connection

# Drop all exeat_app tables
with connection.cursor() as cursor:
    # Drop tables in correct order (reverse of creation)
    tables_to_drop = [
        'exeat_app_exeat',
        'exeat_app_housemistress', 
        'exeat_app_student',
        'exeat_app_securityperson',
        'exeat_app_subadmin',
        'exeat_app_house',
        'exeat_app_customuser',
        'exeat_app_school'
    ]
    
    for table in tables_to_drop:
        try:
            cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
            print(f'✓ Dropped {table}')
        except Exception as e:
            print(f'✗ Could not drop {table}: {e}')
    
    # Clear migration history
    cursor.execute('DELETE FROM django_migrations WHERE app = %s', ['exeat_app'])
    print(f'✓ Cleared migration history')

connection.commit()
print('\n✓ All exeat_app tables cleared, ready for fresh migration')
