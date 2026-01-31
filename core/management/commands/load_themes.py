import json
import os
from django.core.management.base import BaseCommand
from core.models import Template
from django.conf import settings

class Command(BaseCommand):
    help = 'Load themes from themes.json'

    def handle(self, *args, **kwargs):
        json_path = os.path.join(settings.BASE_DIR, 'themes.json')
        
        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
            return

        with open(json_path, 'r') as f:
            themes = json.load(f)

        for theme_data in themes:
            theme, created = Template.objects.update_or_create(
                id_theme=theme_data['id_theme'],
                defaults={
                    'name': theme_data['name'],
                    'category': theme_data['category'],
                    'path': theme_data['path'],
                    'used_count': theme_data.get('used_count', 0)
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created theme: {theme.name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated theme: {theme.name}'))
