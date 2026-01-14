from django.db import models

class Template(models.Model):
    id_theme = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    used_count = models.IntegerField(default=0)
    category = models.CharField(max_length=100)
    path = models.CharField(max_length=255) # Contoh: /templates/rustic-gold

    def __str__(self):
        return self.name

class Song(models.Model):
    id_song = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=100)
    singer = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    path = models.CharField(max_length=500) # URL File MP3

    def __str__(self):
        return f"{self.name} - {self.singer}"