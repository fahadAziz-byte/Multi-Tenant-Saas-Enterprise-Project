import os
import sys
import django

sys.path.append('d:/saas-clean/src')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfehome.settings')
django.setup()

from django.db import connection

def inspect():
    with connection.cursor() as cursor:
        cursor.execute("SELECT schema_name FROM information_schema.schemata;")
        schemas = [row[0] for row in cursor.fetchall()]
        print("Schemas:", schemas)
        
        for schema in schemas:
            if 'tenant' in schema or schema == 'public':
                cursor.execute(f"SET search_path TO '{schema}';")
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s
                """, [schema])
                print(f"--- Tables in {schema} ---")
                tables = [row[0] for row in cursor.fetchall()]
                print(", ".join(tables))

if __name__ == '__main__':
    inspect()
