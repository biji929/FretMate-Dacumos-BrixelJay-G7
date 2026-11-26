from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledAuthenticationForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html', authentication_form=StyledAuthenticationForm), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('guest/', views.guest_login, name='guest_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/guitarist/', views.dashboard_guitarist, name='dashboard_guitarist'),
    path('dashboard/instructor/', views.dashboard_instructor, name='dashboard_instructor'),
    path('instructor/student/<int:student_id>/', views.instructor_student_detail, name='instructor_student_detail'),
    path('api/chord-progress/', views.api_chord_progress, name='api_chord_progress'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('logger/', views.logger, name='logger'),
    path('library/', views.library, name='library'),
    path('songs/', views.songs, name='songs'),
    path('tuner/', views.tuner, name='tuner'),
    path('metronome/', views.metronome, name='metronome'),
    path('tools/', views.tools, name='tools'),
]
