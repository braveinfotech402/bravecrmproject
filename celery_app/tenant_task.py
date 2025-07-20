from celery import Task
from django_tenants.utils import schema_context

class TenantTask(Task):
    def __call__(self, *args, **kwargs):
        schema_name = kwargs.pop('schema_name', 'public')
        with schema_context(schema_name):
            return self.run(*args, **kwargs)
