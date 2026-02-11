import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeat.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

# Mark migration as applied without running it (tables already exist)
with connection.cursor() as cursor:
    cursor.execute('DELETE FROM django_migrations WHERE app = %s', ['exeat_app'])
    print(f'Cleared old migration records')
    
# Insert the applied migration
recorder = MigrationRecorder(connection)
recorder.record_applied('exeat_app', '0001_initial')
print('✓ Migration marked as applied successfully')
