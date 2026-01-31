import os
import django
import json
import sys

# Setup Django Environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Template

def dump_themes():
    themes = Template.objects.all()
    data = []
    for theme in themes:
        data.append({
            "id_theme": theme.id_theme,
            "name": theme.name,
            "category": theme.category,
            "path": theme.path
        })
    
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    dump_themes()
