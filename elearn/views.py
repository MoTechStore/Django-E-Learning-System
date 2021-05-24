from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views import generic
#from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, DetailView 
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, Http404
#from .models import Customer, Profile
from .forms import TakeQuizForm, LearnerSignUpForm, InstructorSignUpForm, QuestionForm, BaseAnswerInlineFormSet, LearnerInterestsForm, LearnerCourse, UserForm, ProfileForm, PostForm
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.urls import reverse
from django.utils import timezone
from django.core import serializers
from django.conf import settings
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from datetime import datetime, date
from django.core.exceptions import ValidationError
from . import models
import operator
import itertools
from django.db.models import Avg, Count, Sum
from django.forms import inlineformset_factory
from .models import TakenQuiz, Profile, Quiz, Question, Answer, Learner, User, Course, Tutorial, Notes, Announcement
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import (AuthenticationForm, UserCreationForm,
                                       PasswordChangeForm)

from django.contrib.auth import update_session_auth_hash                                       


from bootstrap_modal_forms.generic import (
    BSModalLoginView,
    BSModalFormView,
    BSModalCreateView,
    BSModalUpdateView,
    BSModalReadView,
    BSModalDeleteView
)


# Shared Views

def home(request):
	return render(request, 'home.html')

def about(request):
	return render(request, 'about.html')

def services(request):
	return render(request, 'service.html')

def contact(request):
	return render(request, 'contact.html')

def login_form(request):
	return render(request, 'login.html')

def logoutView(request):
	logout(request)
	return redirect('home')

def loginView(request):
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and user.is_active:
			auth.login(request, user)
			if user.is_admin or user.is_superuser:
				return redirect('dashboard')
			elif user.is_instructor:
			    return redirect('instructor')
			elif user.is_learner:
			    return redirect('learner')
			else:
			    return redirect('login_form')
		else:
		    messages.info(request, "Invalid Username or Password")
		    return redirect('login_form')





# Admin Views
def dashboard(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/admin/home.html', context)


class InstructorSignUpView(CreateView):
    model = User
    form_class = InstructorSignUpForm
    template_name = 'dashboard/admin/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Instructor Was Added Successfully')
        return redirect('isign')


class AdminLearner(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'dashboard/admin/learner_signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'Learner Was Added Successfully')
        return redirect('addlearner')



def course(request):
	if request.method == 'POST':
		name = request.POST['name']
		color = request.POST['color']

		a = Course(name=name, color=color)
		a.save()
		messages.success(request, 'New Course Was Registed Successfully')
		return redirect('course')
	else:
	     return render(request, 'dashboard/admin/course.html')	



class AdminCreatePost(CreateView):
    model = Announcement
    form_class = PostForm
    template_name = 'dashboard/admin/post_form.html'
    success_url = reverse_lazy('alpost')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class AdminListTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/tise_list.html'


    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


class ListAllTise(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/admin/list_tises.html'
    context_object_name = 'tises'
    paginated_by = 10


    def get_queryset(self):
        return Announcement.objects.order_by('-id')



class ADeletePost(SuccessMessageMixin, DeleteView):
    model = Announcement
    template_name = 'dashboard/admin/confirm_delete.html'
    success_url = reverse_lazy('alistalltise')
    success_message = "Announcement Was Deleted Successfully"




class ListUserView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'dashboard/admin/list_users.html'
    context_object_name = 'users'
    paginated_by = 10


    def get_queryset(self):
        return User.objects.order_by('-id')



class ADeleteuser(SuccessMessageMixin, DeleteView):
    model = User
    template_name = 'dashboard/admin/confirm_delete2.html'
    success_url = reverse_lazy('aluser')
    success_message = "User Was Deleted Successfully"




def create_user_form(request):
    return render(request, 'dashboard/admin/add_user.html')



def create_user(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password = make_password(password)

        a = User(first_name=first_name, last_name=last_name, username=username, password=password, email=email, is_admin=True)
        a.save()
        messages.success(request, 'Admin Was Created Successfully')
        return redirect('aluser')
    else:
        messages.error(request, 'Admin Was Not Created Successfully')
        return redirect('create_user_form')




def acreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        birth_date = request.POST['birth_date']
        bio = request.POST['bio']
        phonenumber = request.POST['phonenumber']
        city = request.POST['city']
        country = request.POST['country']
        avatar = request.FILES['avatar']
        hobby = request.POST['hobby']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,phonenumber=phonenumber, first_name=first_name, last_name=last_name, bio=bio, birth_date=birth_date, avatar=avatar, city=city, country=country)
        messages.success(request, 'Your Profile Was Created Successfully')
        return redirect('auser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        users = Profile.objects.filter(user_id = user_id)
        users = {'users': users}
        return render(request, 'dashboard/admin/create_profile.html', users)     



def auser_profile(request):
    current_user = request.user
    user_id = current_user.id
    users = Profile.objects.filter(user_id = user_id)
    users = {'users': users}
    return render(request, 'dashboard/admin/user_profile.html', users)     



# Instructor Views
def home_instructor(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()
    context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/instructor/home.html', context)


class QuizCreateView(CreateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/Instructor/quiz_add_form.html'


    def form_valid(self, form):
        quiz = form.save(commit=False)
        quiz.owner = self.request.user
        quiz.save()
        messages.success(self.request, 'Quiz created, Go A Head And Add Questions')
        return redirect('quiz_change', quiz.pk)


class QuizUpateView(UpdateView):
    model = Quiz
    fields = ('name', 'course')
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk', self.object.pk})
        




def question_add(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})




def question_change(request, quiz_pk, question_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk, owner=request.user)
    question = get_object_or_404(Question, pk=question_pk, quiz=quiz)



    AnswerFormatSet = inlineformset_factory (
        Question,
        Answer,
        formset = BaseAnswerInlineFormSet,
        fields = ('text', 'is_correct'),
        min_num = 2,
        validate_min = True,
        max_num = 10,
        validate_max = True
        )

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerFormatSet(request.POST, instance=question)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                formset.save()
                formset.save()
            messages.success(request, 'Question And Answers Saved Successfully')
            return redirect('quiz_change', quiz.pk)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerFormatSet(instance=question)
    return render(request, 'dashboard/instructor/question_change_form.html', {
        'quiz':quiz,
        'question':question,
        'form':form,
        'formset':formset
        })        




class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/instructor/quiz_change_list.html'


    def get_queryset(self):
        queryset = self.request.user.quizzes \
        .select_related('course') \
        .annotate(questions_count = Count('questions', distinct=True)) \
        .annotate(taken_count = Count('taken_quizzes', distinct=True))
        return queryset    


class QuestionDeleteView(DeleteView):
    model = Question
    context_object_name = 'question'
    template_name = 'dashboard/instructor/question_delete_confirm.html'
    pk_url_kwarg = 'question_pk'

    def get_context_data(self, **kwargs):
        question = self.get_object()
        kwargs['quiz'] = question.quiz
        return super().get_context_data(**kwargs)


    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        messages.success(request, 'The Question Was Deleted Successfully')
        return super().delete(request, *args, **kwargs)


    def get_queryset(self):
        return Question.objects.filter(quiz__owner=self.request.user)


    def get_success_url(self):
        question = self.get_object()
        return reverse('quiz_change', kwargs={'pk': question.quiz_id})    



class QuizResultsView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_results.html'


    def get_context_data(self, **kwargs):
        quiz = self.get_object()
        taken_quizzes =quiz.taken_quizzes.select_related('learner__user').order_by('-date')
        total_taken_quizzes = taken_quizzes.count()
        quiz_score = quiz.taken_quizzes.aggregate(average_score=Avg('score'))
        extra_context = {
        'taken_quizzes': taken_quizzes,
        'total_taken_quizzes': total_taken_quizzes,
        'quiz_score':quiz_score
        }

        kwargs.update(extra_context)
        return super().get_context_data(**kwargs)


    def get_queryset(self):
        return self.request.user.quizzes.all()    



class QuizDeleteView(DeleteView):
    model = Quiz
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_delete_confirm.html'
    success_url = reverse_lazy('quiz_change_list')

    def delete(self, request, *args, **kwargs):
        quiz = self.get_object()
        messages.success(request, 'The quiz %s was deleted with success!' % quiz.name)
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.quizzes.all()


def question_add(request, pk):
    # By filtering the quiz by the url keyword argument `pk` and
    # by the owner, which is the logged in user, we are protecting
    # this view at the object-level. Meaning only the owner of
    # quiz will be able to add questions to it.
    quiz = get_object_or_404(Quiz, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'You may now add answers/options to the question.')
            return redirect('question_change', quiz.pk, question.pk)
    else:
        form = QuestionForm()

    return render(request, 'dashboard/instructor/question_add_form.html', {'quiz': quiz, 'form': form})




class QuizUpdateView(UpdateView):
    model = Quiz
    fields = ('name', 'course', )
    context_object_name = 'quiz'
    template_name = 'dashboard/instructor/quiz_change_form.html'


    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.get_object().questions.annotate(answers_count=Count('answers'))
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        '''
        This method is an implicit object-level permission management
        This view will only match the ids of existing quizzes that belongs
        to the logged in user.
        '''
        return self.request.user.quizzes.all()

    def get_success_url(self):
        return reverse('quiz_change', kwargs={'pk': self.object.pk})



 
class CreatePost(CreateView):
    form_class = PostForm
    model = Announcement
    template_name = 'dashboard/instructor/post_form.html'
    success_url = reverse_lazy('llchat')


    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class TiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/instructor/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')


def user_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/instructor/user_profile.html', users)


def create_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name, phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('user_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/instructor/create_profile.html', users)



def tutorial(request):
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}

    return render(request, 'dashboard/instructor/tutorial.html', context)



def publish_tutorial(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        content = request.POST['content']
        thumb = request.FILES['thumb']
        current_user = request.user
        author_id = current_user.id
        print(author_id)
        print(course_id)
        a = Tutorial(title=title, content=content, thumb=thumb, user_id=author_id, course_id=course_id)
        a.save()
        messages.success(request, 'Tutorial was published successfully!')
        return redirect('tutorial')
    else:
        messages.error(request, 'Tutorial was not published successfully!')
        return redirect('tutorial')



def itutorial(request):
   tutorials = Tutorial.objects.all().order_by('-created_at')
   tutorials = {'tutorials':tutorials}
   return render(request, 'dashboard/instructor/list_tutorial.html', tutorials)


class ITutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/instructor/tutorial_detail.html'



class LNotesList(ListView):
    model = Notes
    template_name = 'dashboard/instructor/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')


def iadd_notes(request):
    courses = Course.objects.only('id', 'name')
    context = {'courses':courses}
    return render(request, 'dashboard/instructor/add_notes.html', context)


def publish_notes(request):
    if request.method == 'POST':
        title = request.POST['title']
        course_id = request.POST['course_id']
        cover = request.FILES['cover']
        file = request.FILES['file']
        current_user = request.user
        user_id = current_user.id

        a = Notes(title=title, cover=cover, file=file, user_id=user_id, course_id=course_id)
        a.save()
        messages.success = (request, 'Notes Was Published Successfully')
        return redirect('lnotes')
    else:
        messages.error = (request, 'Notes Was Not Published Successfully')
        return redirect('iadd_notes')


def update_file(request, pk):
    if request.method == 'POST':
        file = request.FILES['file']
        file_name = request.FILES['file'].name

        fs = FileSystemStorage()
        file = fs.save(file.name, file)
        fileurl = fs.url(file)
        file = file_name
        print(file)

        Notes.objects.filter(id = pk).update(file = file)
        messages.success = (request, 'Notes was updated successfully!')
        return redirect('lnotes')
    else:
        return render(request, 'dashboard/instructor/update.html')


# Learner Views
def home_learner(request):
    learner = User.objects.filter(is_learner=True).count()
    instructor = User.objects.filter(is_instructor=True).count()
    course = Course.objects.all().count()
    users = User.objects.all().count()

    context = {'learner':learner, 'course':course, 'instructor':instructor, 'users':users}

    return render(request, 'dashboard/learner/home.html', context)


    
class LearnerSignUpView(CreateView):
    model = User
    form_class = LearnerSignUpForm
    template_name = 'signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'learner'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        #return redirect('learner')
        return redirect('home')



def ltutorial(request):
   tutorials = Tutorial.objects.all().order_by('-created_at')
   tutorials = {'tutorials':tutorials}
   return render(request, 'dashboard/learner/list_tutorial.html', tutorials)


class LLNotesList(ListView):
    model = Notes
    template_name = 'dashboard/learner/list_notes.html'
    context_object_name = 'notes'
    paginate_by = 4


    def get_queryset(self):
        return Notes.objects.order_by('-id')


class ITiseList(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = 'dashboard/learner/tise_list.html'

    def get_queryset(self):
        return Announcement.objects.filter(posted_at__lt=timezone.now()).order_by('posted_at')



def luser_profile(request):
    current_user = request.user
    user_id = current_user.id
    print(user_id)
    users = Profile.objects.filter(user_id=user_id)
    users = {'users':users}
    return render(request, 'dashboard/learner/user_profile.html', users)




def lcreate_profile(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phonenumber = request.POST['phonenumber']
        bio = request.POST['bio']
        city = request.POST['city']
        country = request.POST['country']
        birth_date = request.POST['birth_date']
        avatar = request.FILES['avatar']
        current_user = request.user
        user_id = current_user.id
        print(user_id)

        Profile.objects.filter(id = user_id).create(user_id=user_id,first_name=first_name, last_name=last_name, phonenumber=phonenumber, bio=bio, city=city, country=country, birth_date=birth_date, avatar=avatar)
        messages.success(request, 'Profile was created successfully')
        return redirect('luser_profile')
    else:
        current_user = request.user
        user_id = current_user.id
        print(user_id)
        users = Profile.objects.filter(user_id=user_id)
        users = {'users':users}
        return render(request, 'dashboard/learner/create_profile.html', users)


class LTutorialDetail(LoginRequiredMixin, DetailView):
    model = Tutorial
    template_name = 'dashboard/learner/tutorial_detail.html'



class LearnerInterestsView(UpdateView):
    model = Learner
    form_class = LearnerInterestsForm
    template_name = 'dashboard/learner/interests_form.html'
    success_url = reverse_lazy('lquiz_list')

    def get_object(self):
        return self.request.user.learner

    def form_valid(self, form):
        messages.success(self.request, 'Course Was Updated Successfully')
        return super().form_valid(form)



class LQuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'dashboard/learner/quiz_list.html'

    def get_queryset(self):
        learner = self.request.user.learner
        learner_interests = learner.interests.values_list('pk', flat=True)
        taken_quizzes = learner.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(course__in=learner_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset        



class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'dashboard/learner/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.learner.taken_quizzes \
            .select_related('quiz', 'quiz__course') \
            .order_by('quiz__name')
        return queryset




def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    learner = request.user.learner

    if learner.quizzes.filter(pk=pk).exists():
        return render(request, 'dashboard/learner/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = learner.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                learner_answer = form.save(commit=False)
                learner_answer.student = learner
                learner_answer.save()
                if learner.get_unanswered_questions(quiz).exists():
                    return redirect('take_quiz', pk)
                else:
                    correct_answers = learner.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(learner=learner, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('lquiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'dashboard/learner/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })        