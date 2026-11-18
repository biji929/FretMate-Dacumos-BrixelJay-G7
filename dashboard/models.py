import json
import re
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_GUITARIST = 'GUITARIST'
    ROLE_INSTRUCTOR = 'INSTRUCTOR'
    ROLE_CHOICES = [
        (ROLE_GUITARIST, 'Guitarist'),
        (ROLE_INSTRUCTOR, 'Instructor'),
    ]

    SKILL_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_GUITARIST)
    contact_number = models.CharField(max_length=25, blank=True, default='')
    bio = models.TextField(max_length=500, blank=True, default='')
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default='Beginner')
    weekly_goal_minutes = models.IntegerField(default=120, validators=[MinValueValidator(10), MaxValueValidator(3000)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_instructor(self):
        return self.role == self.ROLE_INSTRUCTOR

    @property
    def is_guitarist(self):
        return self.role == self.ROLE_GUITARIST


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserProfile.ROLE_INSTRUCTOR if (instance.is_superuser or instance.is_staff) else UserProfile.ROLE_GUITARIST
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})


class Chord(models.Model):
    name = models.CharField(max_length=50, unique=True)
    GENRES = [('Rock', 'Rock'), ('Jazz', 'Jazz'), ('Pop', 'Pop'), ('Acoustic', 'Acoustic')]
    genre = models.CharField(max_length=20, choices=GENRES)
    DIFFICULTIES = [('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard')]
    difficulty = models.CharField(max_length=20, choices=DIFFICULTIES)
    diagram_data = models.JSONField()  # e.g., {"frets": [0,2,2,1,0,0], "fingers": [0,1,2,3,0,0], "base_fret": 1}

    def __str__(self):
        return self.name

    @property
    def diagram_json(self):
        return json.dumps(self.diagram_data)

class Tab(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    genre = models.CharField(max_length=20, choices=Chord.GENRES)
    difficulty = models.CharField(max_length=20, choices=Chord.DIFFICULTIES, default='Easy')
    key = models.CharField(max_length=10, default='C')
    content = models.TextField()
    associated_chords = models.ManyToManyField(Chord)
    youtube_url = models.URLField(max_length=300, blank=True, null=True, help_text="YouTube video link for backing track or lesson")
    audio_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct link to MP3 or audio file")

    def __str__(self):
        return f"{self.title} by {self.artist}"

    @property
    def youtube_embed_id(self):
        """Extract YouTube 11-character video ID from common URL formats."""
        if not self.youtube_url:
            return None
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, self.youtube_url)
            if match:
                return match.group(1)
        return None

class PracticeSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    duration_minutes = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(600)])
    FOCUS_AREAS = [('Chords', 'Chords'), ('Songs', 'Songs'), ('Scales', 'Scales'), ('Rhythm', 'Rhythm')]
    focus_area = models.CharField(max_length=20, choices=FOCUS_AREAS)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.duration_minutes}m"

class UserChordProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chord = models.ForeignKey(Chord, on_delete=models.CASCADE)
    STATUSES = [('Learning', 'Learning'), ('Mastered', 'Mastered')]
    status = models.CharField(max_length=20, choices=STATUSES, default='Learning')

    class Meta:
        unique_together = ('user', 'chord')

    def __str__(self):
        return f"{self.user.username} - {self.chord.name} - {self.status}"
