from django.contrib import admin
from .models import UserProfile, Chord, Tab, PracticeSession, UserChordProgress

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'skill_level', 'weekly_goal_minutes', 'created_at')
    list_filter = ('role', 'skill_level')
    search_fields = ('user__username', 'user__email', 'contact_number')

@admin.register(Chord)
class ChordAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'difficulty')
    list_filter = ('genre', 'difficulty')
    search_fields = ('name',)

@admin.register(Tab)
class TabAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'genre', 'difficulty', 'key')
    list_filter = ('genre', 'difficulty', 'key')
    search_fields = ('title', 'artist')

@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'duration_minutes', 'focus_area')
    list_filter = ('focus_area', 'date')
    search_fields = ('user__username', 'notes')

@admin.register(UserChordProgress)
class UserChordProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chord', 'status')
    list_filter = ('status',)

