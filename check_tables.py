import os
import django
import psycopg2

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exeat.settings')
django.setup()

from django.conf import settings
import psycopg2

# Connect directly to check tables
conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST'],
    port=settings.DATABASES['default']['PORT']
)

cursor = conn.cursor()
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name LIKE 'exeat_app%'
""")
tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
