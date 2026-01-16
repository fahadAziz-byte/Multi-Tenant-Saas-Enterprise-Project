from contextlib import contextmanager
from django.db import connection
from .statements import ACTIVATE_SCHEMA_SQL,CREATE_SCHEMA_SQL
from django.core.cache import cache
from django.apps import apps
from django.conf import settings
DEFAULT_SCHEMA = "public"

def does_schema_exists(schema_name):
    exists=False
    with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = %s
                """, [schema_name])
                exists = bool(cursor.fetchone())
    return exists

def activate_tenant_schema(schema_name):
    if not hasattr(connection, "schema_name"):
        connection.schema_name = DEFAULT_SCHEMA

    if connection.schema_name==schema_name:
        print(schema_name,' is already')
        return
    if schema_name != DEFAULT_SCHEMA:
        if not does_schema_exists(schema_name):
            schema_name=DEFAULT_SCHEMA
    with connection.cursor() as cursor:
        cursor.execute(
            ACTIVATE_SCHEMA_SQL.format(schema_name=schema_name)
        )
        connection.schema_name=schema_name
        print('now we have Activated ',schema_name,'Connection schema ',connection.schema_name)
    
@contextmanager
def use_tenant_schema_for_auth(schema_name, create_if_missing=True, revert_public=True):
    try:
        # Create schema if needed
        if create_if_missing and not does_schema_exists(schema_name):
            with connection.cursor() as cursor:
                cursor.execute(
                    CREATE_SCHEMA_SQL.format(schema_name=schema_name)
                )
                print(f"Created schema: {schema_name}")
        
        # ACTIVATE the tenant schema before yielding
        activate_tenant_schema(schema_name)
        print(f"Activated tenant schema: {schema_name}")
        
        yield
    finally:
        # Revert to previous or public schema
        print("In final block of context manager after yielding in use tenant schema for auth")
        if revert_public:
            activate_tenant_schema(DEFAULT_SCHEMA)
@contextmanager
def use_tenant_schema(schema_name, create_if_missing=True, revert_public=True):
    previous_schema = getattr(connection, 'schema_name', DEFAULT_SCHEMA)
    
    try:
        # Create schema if needed
        if create_if_missing and not does_schema_exists(schema_name):
            with connection.cursor() as cursor:
                cursor.execute(
                    CREATE_SCHEMA_SQL.format(schema_name=schema_name)
                )
                print(f"Created schema: {schema_name}")
        
        # ACTIVATE the tenant schema before yielding
        activate_tenant_schema(schema_name)
        print(f"Activated tenant schema: {schema_name}")
        
        yield
    finally:
        # Revert to previous or public schema
        if revert_public:
            activate_tenant_schema(DEFAULT_SCHEMA)
        else:
            activate_tenant_schema(previous_schema)



@contextmanager
def use_public_schema(revert_schema_name=None,revert_schema=False):
    # Save the current schema (so we can restore it later)
    # previous_schema = connection.schema_name
    activate_tenant_schema(DEFAULT_SCHEMA)

    try:
        # Hand control to the caller
        yield
    finally:
        # After the `with` block ends, restore the previous schema
        if revert_schema_name is not None:             
            if revert_schema_name!='public':
                activate_tenant_schema(revert_schema_name)


def get_schema_name(subdomain=None):
    schema_name='public'
    if subdomain is None or subdomain=="localhost" or subdomain==settings.MAIN_SUBDOMAIN:
        activate_tenant_schema(schema_name)
        return schema_name,True,"public"
    # cache_value=cache.get(subdomain)
    # if cache_value:
    #     print('cache hit')
    #     print('cache value : ',cache_value)
    #     return cache_value,True,subdomain
    else :
        with use_public_schema():
            Tenants=apps.get_model('tenants','Tenants')
            try:
                obj=Tenants.objects.get(subdomain=subdomain)
                schema_name=obj.schema_name
            except Tenants.DoesNotExist:
                print(subdomain," does not exist in public schema as a tenant")
                return "public",False,"public"
            except Exception as e:
                print('Exception occured ==>',e)
            # cache_ttl=600  # Cache timeout in seconds (e.g., 10 minutes)
            # cache.set(subdomain,schema_name,cache_ttl)
            # print('cache miss for subdomain ',subdomain,' and schema name : ',schema_name)
    return schema_name,True,subdomain
