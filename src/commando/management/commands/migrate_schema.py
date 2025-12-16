from typing import Any
from django.core.management import BaseCommand
from tenants.tasks import migrate_all_tenant_schema_task

class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
        migrate_all_tenant_schema_task()