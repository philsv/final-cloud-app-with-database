from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Choice, Course, Question, Submission


class ExamResultsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.course = Course.objects.create(name='Test Course', description='Test description')
        self.question = Question.objects.create(course=self.course, question_text='Test question')
        self.correct_choice = Choice.objects.create(question=self.question, choice_text='Correct choice', is_correct=True)
        self.incorrect_choice = Choice.objects.create(question=self.question, choice_text='Incorrect choice', is_correct=False)
        self.submission = Submission.objects.create(enrollment=None)
        self.submission.choices.add(self.correct_choice)
        self.correct_choice_ids = [self.correct_choice.id]
    
    def test_exam_results_correct_answer(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Correct answer: Correct choice')
        self.assertNotContains(response, 'Not Selected: Correct choice')
    
    def test_exam_results_incorrect_answer(self):
        self.client.login(username='testuser', password='testpassword')
        self.submission.choices.add(self.incorrect_choice)
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wrong answer: Incorrect choice')
    
    def test_exam_results_not_selected_correct_answer(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Not Selected: Correct choice')
    
    def test_exam_results_not_selected_incorrect_answer(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incorrect choice')
    
    def test_exam_results_not_logged_in(self):
        response = self.client.get(reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('onlinecourse:login') + '?next=' + reverse('onlinecourse:show_exam_result', args=(self.course.id, self.submission.id)))