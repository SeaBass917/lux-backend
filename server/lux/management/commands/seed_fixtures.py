"""This script sets up all fixtures in the program."""
import json
import os
from django.core import management
from django.core.management.base import BaseCommand
from django.core.serializers import deserialize
from django.db import transaction, connection


class Command(BaseCommand):
    """This command class is used to seed the database with initial data."""
    help = "Seed the database with fixture data from all fixture files."

    @staticmethod
    def update_pk_cursor(table: str):
        """Update the primary key sequence for a table."""
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence"
                f"('{table}', 'id'), "
                "coalesce(max(id), 1), max(id) IS NOT null)"
                f" FROM {table};")

    @staticmethod
    def load_fixture(fixture_path: str):
        """Load a specified fixture."""
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Deserialize the data
        objects = deserialize('json', json.dumps(data))

        # Get or create each object
        count_added = 0
        with transaction.atomic():
            for obj in objects:
                instance = obj.object
                model = instance.__class__
                pk = instance.pk

                defaults = instance.__dict__
                defaults.pop('_state', None)

                try:
                    model.objects.get(pk=pk)
                except model.DoesNotExist:
                    model.objects.create(
                        pk=pk, **defaults)
                    count_added += 1

        # Update the primary key sequence
        table = data[0]['model'].replace('.', '_')
        Command.update_pk_cursor(table)

        # Print the results
        print(
            f"ADDED {count_added} objects" if count_added else "DB already up to date.")

    @staticmethod
    def load_fixtures():
        """Load provider fixtures."""

        # Find all fixtures folders
        fixture_folders = [
            f'{path}/fixtures' for path, dirnames, _ in os.walk('./')
            if 'fixtures' in dirnames]

        # Find all json files under the fixtures folders
        fixture_files = []
        for folder in fixture_folders:
            for dirpath, _, files in os.walk(folder):
                fixture_files.extend(
                    [f"{dirpath}/{filename}"
                     for filename in files if filename.endswith('.json')])

        # Some folders need to go first
        # Specifically the main app
        base_app_fixtures = []
        i = 0
        while i < len(fixture_files):
            if '/lux/' in fixture_files[i]:
                base_app_fixtures.append(fixture_files.pop(i))
            else:
                i += 1

        # Load main app fixtures first
        for fixture in base_app_fixtures:
            print(f"Loading fixture: {fixture}\n  ", end="")
            Command.load_fixture(fixture)

        # Load all json files
        for fixture in fixture_files:
            print(f"Loading fixture: {fixture}\n  ", end="")
            Command.load_fixture(fixture)

    def handle(self, *args, **options):
        """Handle the command."""
        # Run Migrations
        self.stdout.write("Running Migrations")
        management.call_command('migrate')
        self.load_fixtures()
