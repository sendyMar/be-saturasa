from django.core.management.base import BaseCommand
from core.models import Template, Song

class Command(BaseCommand):
    help = 'Seeds database with initial Template and Song data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # Seed Songs
        songs = [
            {
                "id_song": "song_001",
                "name": "Beautiful in White",
                "singer": "Shane Filan",
                "category": "Romantic",
                "path": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            },
            {
                "id_song": "song_002",
                "name": "Perfect",
                "singer": "Ed Sheeran",
                "category": "Pop",
                "path": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
            }
        ]

        for song_data in songs:
            song, created = Song.objects.update_or_create(
                id_song=song_data['id_song'],
                defaults=song_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created song: {song.name}'))
            else:
                self.stdout.write(f'Updated song: {song.name}')

        # Seed Templates
        templates = [
            {
                "id_theme": "theme_001",
                "name": "Rustic Gold Elegant",
                "used_count": 120,
                "category": "Rustic",
                "path": "/templates/rustic-gold" # Local path or slug
            },
            {
                "id_theme": "theme_002",
                "name": "Minimalist White",
                "used_count": 85,
                "category": "Minimalist",
                "path": "/templates/minimalist-white"
            }
        ]

        for template_data in templates:
            tmpl, created = Template.objects.update_or_create(
                id_theme=template_data['id_theme'],
                defaults=template_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created template: {tmpl.name}'))
            else:
                self.stdout.write(f'Updated template: {tmpl.name}')

        self.stdout.write(self.style.SUCCESS('Seeding completed successfully.'))
