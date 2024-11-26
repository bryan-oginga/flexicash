from django.core.management.base import BaseCommand
from django.db.migrations.executor import MigrationExecutor
from django.db import connections

class Command(BaseCommand):
    help = 'Check if migrations are pending'

    def handle(self, *args, **kwargs):
        connection = connections['default']
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()

        # Check if there are any unapplied migrations
        pending_migrations = executor.migration_plan(targets)
        
        if pending_migrations:
            self.stdout.write("Migrations are needed.")
            exit(1)  # Non-zero exit code signals that migrations are needed
        else:
            self.stdout.write("No migrations needed.")
