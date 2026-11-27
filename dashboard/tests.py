from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import PracticeSession, Chord, UserProfile, Tab, UserChordProgress
from django.urls import reverse

class FretMateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

    def test_auth_protection(self):
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_logger_ajax(self):
        response = self.client.post(reverse('logger'), {
            'duration_minutes': 30,
            'focus_area': 'Chords',
            'notes': 'test notes'
        })
        self.assertEqual(response.status_code, 201)
        self.assertTrue(PracticeSession.objects.filter(user=self.user).exists())

    def test_data_isolation(self):
        user2 = User.objects.create_user(username='user2', password='password')
        PracticeSession.objects.create(user=self.user, duration_minutes=10, focus_area='Chords')
        PracticeSession.objects.create(user=user2, duration_minutes=20, focus_area='Chords')
        self.assertEqual(PracticeSession.objects.filter(user=self.user).count(), 1)
        self.assertEqual(PracticeSession.objects.filter(user=user2).count(), 1)

    def test_songs_view(self):
        response = self.client.get(reverse('songs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'songs.html')

    def test_add_song_post(self):
        chord = Chord.objects.create(name='TestChord', genre='Rock', difficulty='Easy', diagram_data={'frets': [0, 2, 2, 0, 0, 0]})
        response = self.client.post(reverse('songs'), {
            'title': 'My New Song',
            'artist': 'Awesome Band',
            'genre': 'Rock',
            'difficulty': 'Easy',
            'key': 'G',
            'associated_chords': [chord.id],
            'content': 'G   C\nTest song lyrics'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tab.objects.filter(title='My New Song', artist='Awesome Band').exists())

    def test_registration_with_email_and_role(self):
        self.client.logout()
        get_res = self.client.get(reverse('register'))
        self.assertNotIn('first_name', get_res.context['form'].fields)
        self.assertNotIn('last_name', get_res.context['form'].fields)

        response = self.client.post(reverse('register'), {
            'username': 'newguitarist',
            'email': 'carlos@example.com',
            'role': UserProfile.ROLE_GUITARIST,
            'password1': 'StrongP@ssw0rd123!',
            'password2': 'StrongP@ssw0rd123!',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newguitarist')
        self.assertEqual(user.email, 'carlos@example.com')
        self.assertEqual(user.profile.role, UserProfile.ROLE_GUITARIST)

    def test_registration_duplicate_email_rejected(self):
        User.objects.create_user(username='existing', email='unique@example.com', password='password123')
        self.client.logout()
        response = self.client.post(reverse('register'), {
            'username': 'differentuser',
            'email': 'unique@example.com',
            'role': UserProfile.ROLE_GUITARIST,
            'password1': 'StrongP@ssw0rd123!',
            'password2': 'StrongP@ssw0rd123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')

    def test_role_based_dashboard_dispatch(self):
        # Guitarist user dispatch
        self.user.profile.role = UserProfile.ROLE_GUITARIST
        self.user.profile.save()
        res_guitarist = self.client.get(reverse('dashboard'))
        self.assertRedirects(res_guitarist, reverse('dashboard_guitarist'))

        # Instructor user dispatch
        self.user.profile.role = UserProfile.ROLE_INSTRUCTOR
        self.user.profile.save()
        res_instructor = self.client.get(reverse('dashboard'))
        self.assertRedirects(res_instructor, reverse('dashboard_instructor'))

    def test_role_url_protection_blocks_guitarist(self):
        self.user.profile.role = UserProfile.ROLE_GUITARIST
        self.user.profile.save()
        # Guitarist attempts to access Instructor dashboard URL directly
        response = self.client.get(reverse('dashboard_instructor'))
        self.assertRedirects(response, reverse('dashboard_guitarist'))

    def test_user_profile_view_and_edit(self):
        # View profile
        get_res = self.client.get(reverse('profile'))
        self.assertEqual(get_res.status_code, 200)
        self.assertTemplateUsed(get_res, 'profile.html')

        # Edit profile details
        post_res = self.client.post(reverse('profile'), {
            'first_name': 'Brixel',
            'last_name': 'Dacumos',
            'email': 'biji.guitar@example.com',
            'contact_number': '+63 912 345 6789',
            'bio': 'Passionate acoustic and electric guitarist.',
            'skill_level': 'Intermediate',
            'weekly_goal_minutes': 180,
        })
        self.assertEqual(post_res.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Brixel')
        self.assertEqual(self.user.last_name, 'Dacumos')
        self.assertEqual(self.user.email, 'biji.guitar@example.com')
        self.assertEqual(self.user.profile.contact_number, '+63 912 345 6789')
        self.assertEqual(self.user.profile.skill_level, 'Intermediate')
        self.assertEqual(self.user.profile.weekly_goal_minutes, 180)

    def test_api_chord_progress_learning_and_mastered(self):
        chord = Chord.objects.create(name='D Major', genre='Pop', difficulty='Easy', diagram_data={'frets': [-1, -1, 0, 2, 3, 2]})
        # Mark as Learning
        res = self.client.post(reverse('api_chord_progress'), {
            'chord_id': chord.id,
            'status': 'Learning'
        }, content_type='application/json')
        self.assertEqual(res.status_code, 200)
        self.assertTrue(UserChordProgress.objects.filter(user=self.user, chord=chord, status='Learning').exists())

        # Update to Mastered
        res_mastered = self.client.post(reverse('api_chord_progress'), {
            'chord_id': chord.id,
            'status': 'Mastered'
        }, content_type='application/json')
        self.assertEqual(res_mastered.status_code, 200)
        self.assertTrue(UserChordProgress.objects.filter(user=self.user, chord=chord, status='Mastered').exists())

    def test_api_chord_progress_reset(self):
        chord = Chord.objects.create(name='E Minor', genre='Rock', difficulty='Easy', diagram_data={'frets': [0, 2, 2, 0, 0, 0]})
        UserChordProgress.objects.create(user=self.user, chord=chord, status='Learning')
        res_reset = self.client.post(reverse('api_chord_progress'), {
            'chord_id': chord.id,
            'status': 'None'
        }, content_type='application/json')
        self.assertEqual(res_reset.status_code, 200)
        self.assertFalse(UserChordProgress.objects.filter(user=self.user, chord=chord).exists())

    def test_instructor_student_detail_view(self):
        self.user.profile.role = UserProfile.ROLE_INSTRUCTOR
        self.user.profile.save()
        student = User.objects.create_user(username='student1', password='password123')
        PracticeSession.objects.create(user=student, duration_minutes=45, focus_area='Scales')

        response = self.client.get(reverse('instructor_student_detail', kwargs={'student_id': student.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'instructor_student_detail.html')
        self.assertContains(response, 'student1')

    def test_instructor_student_detail_blocked_for_guitarist(self):
        self.user.profile.role = UserProfile.ROLE_GUITARIST
        self.user.profile.save()
        student = User.objects.create_user(username='student2', password='password123')
        response = self.client.get(reverse('instructor_student_detail', kwargs={'student_id': student.id}))
        self.assertRedirects(response, reverse('dashboard_guitarist'))

    # ================= CORE FEATURE CRUD TESTS (VERTICAL SLICE) =================
    def test_get_practice_session(self):
        session = PracticeSession.objects.create(
            user=self.user,
            duration_minutes=45,
            focus_area='Scales',
            notes='Dorian mode practice'
        )
        response = self.client.get(reverse('get_practice_session', kwargs={'session_id': session.id}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['session']['duration_minutes'], 45)
        self.assertEqual(data['session']['focus_area'], 'Scales')
        self.assertEqual(data['session']['notes'], 'Dorian mode practice')

    def test_update_practice_session(self):
        session = PracticeSession.objects.create(
            user=self.user,
            duration_minutes=30,
            focus_area='Chords',
            notes='Initial chord drills'
        )
        response = self.client.post(
            reverse('update_practice_session', kwargs={'session_id': session.id}),
            {
                'duration_minutes': 60,
                'focus_area': 'Songs',
                'notes': 'Updated to full song rehearsal'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        session.refresh_from_db()
        self.assertEqual(session.duration_minutes, 60)
        self.assertEqual(session.focus_area, 'Songs')
        self.assertEqual(session.notes, 'Updated to full song rehearsal')

    def test_delete_practice_session(self):
        session = PracticeSession.objects.create(
            user=self.user,
            duration_minutes=25,
            focus_area='Chords',
            notes='Session to be deleted'
        )
        self.assertTrue(PracticeSession.objects.filter(id=session.id).exists())
        response = self.client.post(
            reverse('delete_practice_session', kwargs={'session_id': session.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(PracticeSession.objects.filter(id=session.id).exists())

    def test_practice_session_data_isolation_crud(self):
        other_user = User.objects.create_user(username='otherguitarist', password='password123')
        other_session = PracticeSession.objects.create(
            user=other_user,
            duration_minutes=50,
            focus_area='Songs',
            notes='Secret other notes'
        )
        # Attempt to read other user's session
        get_res = self.client.get(reverse('get_practice_session', kwargs={'session_id': other_session.id}))
        self.assertEqual(get_res.status_code, 404)

        # Attempt to update other user's session
        update_res = self.client.post(
            reverse('update_practice_session', kwargs={'session_id': other_session.id}),
            {'duration_minutes': 10, 'focus_area': 'Scales', 'notes': 'Hacked notes'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(update_res.status_code, 404)
        other_session.refresh_from_db()
        self.assertEqual(other_session.duration_minutes, 50)

        # Attempt to delete other user's session
        del_res = self.client.post(
            reverse('delete_practice_session', kwargs={'session_id': other_session.id}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(del_res.status_code, 404)
        self.assertTrue(PracticeSession.objects.filter(id=other_session.id).exists())

    def test_export_practice_csv(self):
        PracticeSession.objects.create(user=self.user, duration_minutes=35, focus_area='Chords', notes='CSV drill')
        response = self.client.get(reverse('export_practice_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(f'attachment; filename="fretmate_practice_{self.user.username}.csv"', response['Content-Disposition'])
        self.assertIn('CSV drill', response.content.decode('utf-8'))

    def test_guest_can_access_register_and_upgrade_account(self):
        self.client.logout()
        # Sign in as guest
        guest_res = self.client.post(reverse('guest_login'))
        self.assertEqual(guest_res.status_code, 302)
        guest_user = User.objects.get(username__startswith='guest_')

        # Create guest practice session and chord progress
        chord = Chord.objects.create(name='A Minor', genre='Pop', difficulty='Easy', diagram_data={'frets': [-1, 0, 2, 2, 1, 0]})
        PracticeSession.objects.create(user=guest_user, duration_minutes=20, focus_area='Chords', notes='Guest session')
        UserChordProgress.objects.create(user=guest_user, chord=chord, status='Learning')

        # Guest clicking "Register Free" must load the register page (200), not redirect to dashboard
        get_res = self.client.get(reverse('register'))
        self.assertEqual(get_res.status_code, 200)
        self.assertTemplateUsed(get_res, 'registration/register.html')
        self.assertTrue(get_res.context['is_guest'])

        # Submit registration to permanently save guest progress
        post_res = self.client.post(reverse('register'), {
            'username': 'upgradedguitarist',
            'email': 'alex@example.com',
            'role': UserProfile.ROLE_GUITARIST,
            'password1': 'StrongP@ssw0rd123!',
            'password2': 'StrongP@ssw0rd123!',
        })
        self.assertEqual(post_res.status_code, 302)
        new_user = User.objects.get(username='upgradedguitarist')
        # Guest account removed and progress migrated to new user
        self.assertFalse(User.objects.filter(id=guest_user.id).exists())
        self.assertTrue(PracticeSession.objects.filter(user=new_user, notes='Guest session').exists())
        self.assertTrue(UserChordProgress.objects.filter(user=new_user, chord=chord, status='Learning').exists())

    def test_regular_authenticated_user_redirected_from_register(self):
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)

    def test_login_asks_role_first_and_enforces_role_match(self):
        self.client.logout()
        # Step 1: GET /login/ asks Student or Instructor first
        get_res = self.client.get(reverse('login'))
        self.assertEqual(get_res.status_code, 200)
        self.assertContains(get_res, 'chooseStudentBtn')
        self.assertContains(get_res, 'chooseInstructorBtn')
        self.assertContains(get_res, 'name="login_role"')

        # Setup a student and an instructor account
        self.user.profile.role = UserProfile.ROLE_GUITARIST
        self.user.profile.save()
        instructor = User.objects.create_user(username='teacher1', password='password')
        instructor.profile.role = UserProfile.ROLE_INSTRUCTOR
        instructor.profile.save()

        # Student trying to sign in via Instructor portal is rejected
        mismatch_student = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password',
            'login_role': UserProfile.ROLE_INSTRUCTOR,
        })
        self.assertEqual(mismatch_student.status_code, 200)
        self.assertContains(mismatch_student, 'registered as a Student')

        # Instructor trying to sign in via Student portal is rejected
        mismatch_instructor = self.client.post(reverse('login'), {
            'username': 'teacher1',
            'password': 'password',
            'login_role': UserProfile.ROLE_GUITARIST,
        })
        self.assertEqual(mismatch_instructor.status_code, 200)
        self.assertContains(mismatch_instructor, 'registered as an Instructor')

        # Matching role sign-in succeeds for Student
        ok_student = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password',
            'login_role': UserProfile.ROLE_GUITARIST,
        })
        self.assertEqual(ok_student.status_code, 302)

        # Matching role sign-in succeeds for Instructor
        self.client.logout()
        ok_instructor = self.client.post(reverse('login'), {
            'username': 'teacher1',
            'password': 'password',
            'login_role': UserProfile.ROLE_INSTRUCTOR,
        })
        self.assertEqual(ok_instructor.status_code, 302)



