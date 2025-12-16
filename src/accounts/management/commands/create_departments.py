from django.core.management.base import BaseCommand
from accounts.models import Department
from helpers.db.schemas import use_tenant_schema_for_auth
from tenants.models import Tenants

class Command(BaseCommand):
    help = 'Create default departments for a tenant'

    def add_arguments(self, parser):
        parser.add_argument('subdomain', type=str, help='Tenant subdomain')

    def handle(self, *args, **options):
        subdomain = options['subdomain']
        
        try:
            # Get tenant from public schema
            with use_tenant_schema_for_auth("public", False, False):
                tenant = Tenants.objects.get(subdomain=subdomain)
            
            self.stdout.write(f'Setting up departments for tenant: {tenant.subdomain}')
            
            # Activate tenant schema and create departments
            with use_tenant_schema_for_auth(tenant.schema_name, False, False):
                # Create default departments
                departments = [
                    {'name': 'Engineering', 'description': 'Software development and technical teams'},
                    {'name': 'Sales', 'description': 'Sales and business development'},
                    {'name': 'Marketing', 'description': 'Marketing and communications'},
                    {'name': 'Operations', 'description': 'Operations and logistics'},
                    {'name': 'Human Resources', 'description': 'HR and people operations'},
                    {'name': 'Finance', 'description': 'Finance and accounting'},
                    {'name': 'Customer Support', 'description': 'Customer service and support'},
                ]
                
                created_count = 0
                existing_count = 0
                
                for dept_data in departments:
                    dept, created = Department.objects.get_or_create(
                        name=dept_data['name'],
                        defaults={'description': dept_data['description']}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {dept.name}'))
                    else:
                        existing_count += 1
                        self.stdout.write(self.style.WARNING(f'  - Already exists: {dept.name}'))
                
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS(f'Summary:'))
                self.stdout.write(self.style.SUCCESS(f'  Created: {created_count} departments'))
                self.stdout.write(self.style.WARNING(f'  Existing: {existing_count} departments'))
                self.stdout.write(self.style.SUCCESS(f'  Total: {Department.objects.count()} departments'))
        
        except Tenants.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'✗ Tenant with subdomain "{subdomain}" not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            import traceback
            traceback.print_exc()