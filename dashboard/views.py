import json
import csv
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.utils.crypto import get_random_string
from django.views.decorators.http import require_POST
from .forms import RegistrationForm, UserProfileUpdateForm
from .forms_session import PracticeSessionForm
from .forms_song import SongForm
from .models import PracticeSession, Chord, Tab, UserChordProgress, UserProfile
from django.db.models import Sum, Count, Q
from datetime import date, timedelta

User = get_user_model()

def role_required(allowed_roles):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Prevents unauthorized access across role boundaries (e.g. Guitarist typing Instructor URL).
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            profile = getattr(request.user, 'profile', None)
            user_role = profile.role if profile else UserProfile.ROLE_GUITARIST
            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f"Access Denied: You do not have permission to access the {allowed_roles[0].title()} Portal."
                )
                if user_role == UserProfile.ROLE_INSTRUCTOR:
                    return redirect('dashboard_instructor')
                return redirect('dashboard_guitarist')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def home(request):
    return render(request, 'landing.html')

@require_POST
def guest_login(request):
    username = f'guest_{get_random_string(8)}'
    user = User.objects.create_user(username=username)
    user.set_unusable_password()
    user.save()
    login(request, user)
    return redirect('dashboard')

def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been signed out.")
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_display = user.profile.get_role_display() if hasattr(user, 'profile') else 'Guitarist'
            messages.success(request, f'Welcome to FretMate, {user.first_name}! Your {role_display} account was created successfully.')
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Registration failed. Please review the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    """Dispatcher: routes user to the dedicated dashboard for their specific role."""
    profile = getattr(request.user, 'profile', None)
    if profile and profile.is_instructor:
        return redirect('dashboard_instructor')
    return redirect('dashboard_guitarist')

@role_required([UserProfile.ROLE_GUITARIST])
def dashboard_guitarist(request):
    user = request.user
    total_minutes = PracticeSession.objects.filter(user=user).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    total_chords_mastered = UserChordProgress.objects.filter(user=user, status='Mastered').count()
    total_chords = Chord.objects.count()

    profile = getattr(user, 'profile', None)
    weekly_goal = profile.weekly_goal_minutes if profile else 120

    today = date.today()
    monday = today - timedelta(days=today.weekday())
    weekly_minutes = PracticeSession.objects.filter(user=user, date__gte=monday).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    goal_percent = min(100, int((weekly_minutes / weekly_goal) * 100)) if weekly_goal > 0 else 0

    sessions_dates = set(PracticeSession.objects.filter(user=user).values_list('date', flat=True))
    streak = 0
    check_day = today
    if check_day not in sessions_dates:
        check_day = today - timedelta(days=1)
    while check_day in sessions_dates:
        streak += 1
        check_day -= timedelta(days=1)

    focus_counts = {
        'Chords': PracticeSession.objects.filter(user=user, focus_area='Chords').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Songs': PracticeSession.objects.filter(user=user, focus_area='Songs').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Scales': PracticeSession.objects.filter(user=user, focus_area='Scales').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Rhythm': PracticeSession.objects.filter(user=user, focus_area='Rhythm').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
    }

    days_labels = []
    days_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days_labels.append(day.strftime('%a'))
        day_mins = PracticeSession.objects.filter(user=user, date=day).aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
        days_data.append(day_mins)

    recent_sessions = PracticeSession.objects.filter(user=user).order_by('-id')[:5]

    return render(request, 'dashboard_guitarist.html', {
        'total_minutes': total_minutes,
        'streak': streak,
        'chords_mastered': total_chords_mastered,
        'total_chords': total_chords,
        'weekly_goal': weekly_goal,
        'weekly_minutes': weekly_minutes,
        'goal_percent': goal_percent,
        'focus_counts': focus_counts,
        'days_labels': days_labels,
        'days_data': days_data,
        'recent_sessions': recent_sessions,
    })

@role_required([UserProfile.ROLE_INSTRUCTOR])
def dashboard_instructor(request):
    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_GUITARIST).count()
    total_songs = Tab.objects.count()
    total_chords = Chord.objects.count()
    total_practice_mins = PracticeSession.objects.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    total_sessions = PracticeSession.objects.count()

    students = UserProfile.objects.filter(role=UserProfile.ROLE_GUITARIST).select_related('user').order_by('-created_at')[:15]
    recent_activity = PracticeSession.objects.select_related('user').order_by('-id')[:8]

    return render(request, 'dashboard_instructor.html', {
        'total_students': total_students,
        'total_songs': total_songs,
        'total_chords': total_chords,
        'total_practice_mins': total_practice_mins,
        'total_sessions': total_sessions,
        'students': students,
        'recent_activity': recent_activity,
    })

@role_required([UserProfile.ROLE_INSTRUCTOR])
def instructor_student_detail(request, student_id):
    student = get_object_or_404(User, id=student_id)
    profile = getattr(student, 'profile', None)

    sessions = PracticeSession.objects.filter(user=student).order_by('-date', '-id')
    total_minutes = sessions.aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    total_sessions = sessions.count()

    progress_qs = UserChordProgress.objects.filter(user=student).select_related('chord')
    mastered_chords = [p.chord for p in progress_qs if p.status == 'Mastered']
    learning_chords = [p.chord for p in progress_qs if p.status == 'Learning']

    focus_breakdown = {
        'Chords': sessions.filter(focus_area='Chords').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Songs': sessions.filter(focus_area='Songs').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Scales': sessions.filter(focus_area='Scales').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
        'Rhythm': sessions.filter(focus_area='Rhythm').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0,
    }

    return render(request, 'instructor_student_detail.html', {
        'student': student,
        'profile': profile,
        'sessions': sessions,
        'total_minutes': total_minutes,
        'total_sessions': total_sessions,
        'mastered_chords': mastered_chords,
        'learning_chords': learning_chords,
        'focus_breakdown': focus_breakdown,
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile details have been successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors in the profile form.')
    else:
        form = UserProfileUpdateForm(user=request.user)

    return render(request, 'profile.html', {'form': form})


@login_required
def logger(request):
    if request.method == 'POST':
        form = PracticeSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            return JsonResponse({
                'status': 'success',
                'session': {
                    'date': session.date.strftime('%b %d, %Y') if session.date else 'Today',
                    'duration_minutes': session.duration_minutes,
                    'focus_area': session.focus_area,
                    'notes': session.notes or ''
                }
            }, status=201)
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    form = PracticeSessionForm()
    recent_sessions = PracticeSession.objects.filter(user=request.user).order_by('-id')[:10]
    return render(request, 'logger.html', {'form': form, 'recent_sessions': recent_sessions})


@login_required
def export_practice_csv(request):
    """Exports user's complete practice session history as a CSV file."""
    sessions = PracticeSession.objects.filter(user=request.user).order_by('-date', '-id')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="fretmate_practice_{request.user.username}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Session ID', 'Date', 'Duration (Minutes)', 'Focus Area', 'Notes'])

    for s in sessions:
        writer.writerow([
            s.id,
            s.date.strftime('%Y-%m-%d') if s.date else '',
            s.duration_minutes,
            s.focus_area,
            s.notes or ''
        ])

    return response

KEY_DEFINITIONS = {
    'C': [
        (1, 'I', 'Tonic', 'C Major'),
        (2, 'ii', 'Supertonic', 'D Minor'),
        (3, 'iii', 'Mediant', 'E Minor'),
        (4, 'IV', 'Subdominant', 'F Major'),
        (5, 'V', 'Dominant', 'G Major'),
        (6, 'vi', 'Submediant', 'A Minor'),
        (7, 'vii°', 'Leading Tone', 'B Diminished'),
    ],
    'G': [
        (1, 'I', 'Tonic', 'G Major'),
        (2, 'ii', 'Supertonic', 'A Minor'),
        (3, 'iii', 'Mediant', 'B Minor'),
        (4, 'IV', 'Subdominant', 'C Major'),
        (5, 'V', 'Dominant', 'D Major'),
        (6, 'vi', 'Submediant', 'E Minor'),
        (7, 'vii°', 'Leading Tone', 'F# Diminished'),
    ],
    'D': [
        (1, 'I', 'Tonic', 'D Major'),
        (2, 'ii', 'Supertonic', 'E Minor'),
        (3, 'iii', 'Mediant', 'F# Minor'),
        (4, 'IV', 'Subdominant', 'G Major'),
        (5, 'V', 'Dominant', 'A Major'),
        (6, 'vi', 'Submediant', 'B Minor'),
        (7, 'vii°', 'Leading Tone', 'C# Diminished'),
    ],
    'A': [
        (1, 'I', 'Tonic', 'A Major'),
        (2, 'ii', 'Supertonic', 'B Minor'),
        (3, 'iii', 'Mediant', 'C# Minor'),
        (4, 'IV', 'Subdominant', 'D Major'),
        (5, 'V', 'Dominant', 'E Major'),
        (6, 'vi', 'Submediant', 'F# Minor'),
        (7, 'vii°', 'Leading Tone', 'G# Diminished'),
    ],
    'E': [
        (1, 'I', 'Tonic', 'E Major'),
        (2, 'ii', 'Supertonic', 'F# Minor'),
        (3, 'iii', 'Mediant', 'G# Minor'),
        (4, 'IV', 'Subdominant', 'A Major'),
        (5, 'V', 'Dominant', 'B Major'),
        (6, 'vi', 'Submediant', 'C# Minor'),
        (7, 'vii°', 'Leading Tone', 'D# Diminished'),
    ],
    'B': [
        (1, 'I', 'Tonic', 'B Major'),
        (2, 'ii', 'Supertonic', 'C# Minor'),
        (3, 'iii', 'Mediant', 'D# Minor'),
        (4, 'IV', 'Subdominant', 'E Major'),
        (5, 'V', 'Dominant', 'F# Major'),
        (6, 'vi', 'Submediant', 'G# Minor'),
        (7, 'vii°', 'Leading Tone', 'A# Diminished'),
    ],
    'F': [
        (1, 'I', 'Tonic', 'F Major'),
        (2, 'ii', 'Supertonic', 'G Minor'),
        (3, 'iii', 'Mediant', 'A Minor'),
        (4, 'IV', 'Subdominant', 'Bb Major'),
        (5, 'V', 'Dominant', 'C Major'),
        (6, 'vi', 'Submediant', 'D Minor'),
        (7, 'vii°', 'Leading Tone', 'E Diminished'),
    ],
    'Bb': [
        (1, 'I', 'Tonic', 'Bb Major'),
        (2, 'ii', 'Supertonic', 'C Minor'),
        (3, 'iii', 'Mediant', 'D Minor'),
        (4, 'IV', 'Subdominant', 'Eb Major'),
        (5, 'V', 'Dominant', 'F Major'),
        (6, 'vi', 'Submediant', 'G Minor'),
        (7, 'vii°', 'Leading Tone', 'A Diminished'),
    ],
    'Eb': [
        (1, 'I', 'Tonic', 'Eb Major'),
        (2, 'ii', 'Supertonic', 'F Minor'),
        (3, 'iii', 'Mediant', 'G Minor'),
        (4, 'IV', 'Subdominant', 'Ab Major'),
        (5, 'V', 'Dominant', 'Bb Major'),
        (6, 'vi', 'Submediant', 'C Minor'),
        (7, 'vii°', 'Leading Tone', 'D Diminished'),
    ],
    'Ab': [
        (1, 'I', 'Tonic', 'Ab Major'),
        (2, 'ii', 'Supertonic', 'Bb Minor'),
        (3, 'iii', 'Mediant', 'C Minor'),
        (4, 'IV', 'Subdominant', 'Db Major'),
        (5, 'V', 'Dominant', 'Eb Major'),
        (6, 'vi', 'Submediant', 'F Minor'),
        (7, 'vii°', 'Leading Tone', 'G Diminished'),
    ],
    'Db': [
        (1, 'I', 'Tonic', 'Db Major'),
        (2, 'ii', 'Supertonic', 'Eb Minor'),
        (3, 'iii', 'Mediant', 'F Minor'),
        (4, 'IV', 'Subdominant', 'Gb Major'),
        (5, 'V', 'Dominant', 'Ab Major'),
        (6, 'vi', 'Submediant', 'Bb Minor'),
        (7, 'vii°', 'Leading Tone', 'C Diminished'),
    ],
    'F#': [
        (1, 'I', 'Tonic', 'F# Major'),
        (2, 'ii', 'Supertonic', 'G# Minor'),
        (3, 'iii', 'Mediant', 'A# Minor'),
        (4, 'IV', 'Subdominant', 'B Major'),
        (5, 'V', 'Dominant', 'C# Major'),
        (6, 'vi', 'Submediant', 'D# Minor'),
        (7, 'vii°', 'Leading Tone', 'F Diminished'),
    ]
}

@login_required
def library(request):
    all_chords = Chord.objects.all().order_by('name')
    tabs = Tab.objects.all().prefetch_related('associated_chords')

    genre = request.GET.get('genre')
    difficulty = request.GET.get('difficulty')

    chords = all_chords
    if genre:
        chords = chords.filter(genre=genre)
        tabs = tabs.filter(genre=genre)
    if difficulty:
        chords = chords.filter(difficulty=difficulty)

    user_progress = UserChordProgress.objects.filter(user=request.user)
    mastered_ids = set(user_progress.filter(status='Mastered').values_list('chord_id', flat=True))
    learning_ids = set(user_progress.filter(status='Learning').values_list('chord_id', flat=True))

    all_chords_dict = {c.name: c for c in all_chords}
    available_keys = list(KEY_DEFINITIONS.keys())
    selected_key = request.GET.get('key', 'C')
    if selected_key not in KEY_DEFINITIONS:
        selected_key = 'C'

    key_chords = []
    for degree, roman, function_name, chord_name in KEY_DEFINITIONS[selected_key]:
        chord_obj = all_chords_dict.get(chord_name)
        key_chords.append({
            'degree': degree,
            'roman': roman,
            'function': function_name,
            'name': chord_name,
            'chord': chord_obj,
        })

    # Progressions for the selected key
    deg_map = {item['degree']: item['name'] for item in key_chords}
    common_progressions = [
        {'name': 'Pop / Rock Hit', 'formula': '1 - 5 - 6 - 4', 'chords': [deg_map.get(1), deg_map.get(5), deg_map.get(6), deg_map.get(4)]},
        {'name': 'Classic Blues / Rock', 'formula': '1 - 4 - 5', 'chords': [deg_map.get(1), deg_map.get(4), deg_map.get(5)]},
        {'name': 'Jazz & Pop Cadence', 'formula': '2 - 5 - 1', 'chords': [deg_map.get(2), deg_map.get(5), deg_map.get(1)]},
        {'name': 'Doo-Wop 50s Ballad', 'formula': '1 - 6 - 4 - 5', 'chords': [deg_map.get(1), deg_map.get(6), deg_map.get(4), deg_map.get(5)]},
    ]

    return render(request, 'library.html', {
        'chords': chords,
        'tabs': tabs,
        'user_progress': user_progress,
        'mastered_ids': mastered_ids,
        'learning_ids': learning_ids,
        'selected_genre': genre or '',
        'selected_difficulty': difficulty or '',
        'available_keys': available_keys,
        'selected_key': selected_key,
        'key_chords': key_chords,
        'common_progressions': common_progressions,
    })

@require_POST
@login_required
def api_chord_progress(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    chord_id = data.get('chord_id')
    status = data.get('status')

    if not chord_id:
        return JsonResponse({'status': 'error', 'message': 'chord_id is required'}, status=400)

    try:
        chord = Chord.objects.get(id=chord_id)
    except Chord.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Chord not found'}, status=404)

    if status in ['Learning', 'Mastered']:
        progress, _ = UserChordProgress.objects.update_or_create(
            user=request.user,
            chord=chord,
            defaults={'status': status}
        )
        return JsonResponse({
            'status': 'success',
            'chord_id': chord.id,
            'chord_name': chord.name,
            'status': progress.status,
            'message': f'"{chord.name}" marked as {progress.status}!'
        })
    elif status in ['None', '', 'reset']:
        UserChordProgress.objects.filter(user=request.user, chord=chord).delete()
        return JsonResponse({
            'status': 'success',
            'chord_id': chord.id,
            'chord_name': chord.name,
            'status': None,
            'message': f'"{chord.name}" progress reset.'
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid status. Choose Learning, Mastered, or None.'}, status=400)

@login_required
def songs(request):
    if request.method == 'POST':
        form = SongForm(request.POST)
        if form.is_valid():
            new_song = form.save()
            messages.success(request, f'"{new_song.title}" by {new_song.artist} has been added to your Song Library!')
            return redirect('songs')
        else:
            messages.error(request, 'Could not add song. Please check the form errors below.')
    else:
        form = SongForm()

    song_list = Tab.objects.all().prefetch_related('associated_chords').order_by('title')

    q = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()
    key = request.GET.get('key', '').strip()

    if q:
        song_list = song_list.filter(Q(title__icontains=q) | Q(artist__icontains=q) | Q(content__icontains=q))
    if genre:
        song_list = song_list.filter(genre=genre)
    if difficulty:
        song_list = song_list.filter(difficulty=difficulty)
    if key:
        song_list = song_list.filter(key=key)

    available_keys = sorted(list(set(Tab.objects.values_list('key', flat=True).distinct())))
    all_chords = Chord.objects.all().order_by('name')

    return render(request, 'songs.html', {
        'songs': song_list,
        'form': form,
        'all_chords': all_chords,
        'search_query': q,
        'selected_genre': genre,
        'selected_difficulty': difficulty,
        'selected_key': key,
        'available_keys': available_keys,
        'total_songs': Tab.objects.count(),
    })

@login_required
def tuner(request):
    return render(request, 'tuner.html')

@login_required
def metronome(request):
    return render(request, 'metronome.html')

@login_required
def tools(request):
    return redirect('tuner')

@login_required
def settings(request):
    return redirect('profile')
