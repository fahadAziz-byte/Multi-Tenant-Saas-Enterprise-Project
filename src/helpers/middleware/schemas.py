from django.http import HttpResponse
from helpers.db.schemas import activate_tenant_schema,get_schema_name


class SchemaTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]

        parts = host.split('.')

        if len(parts) < 3:
            subdomain = None
        else:
            subdomain = parts[0]

        schema_name, valid_tenant, subdomain = get_schema_name(subdomain)

        activate_tenant_schema(schema_name)

        request.subdomain = subdomain
        request.valid_tenant = valid_tenant

        response = self.get_response(request)
        return response


    

    