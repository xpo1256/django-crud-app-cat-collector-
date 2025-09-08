
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from .models import Cat, Toy
from .forms import FeedingForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.
# def home(request):
#     # Send a simple HTML response
#     return render(request, "home.html")
class Home(LoginView):
    template_name = 'home.html'
def about(request):
    return render(request, 'about.html')
class Cat:
    def __init__(self, name, breed, description, age):
        self.name = name
        self.breed = breed
        self.description = description
        self.age = age
# Create a list of Cat instances
from django.shortcuts import render
from .models import Cat
@login_required
def cat_index(request):
    cats = Cat.objects.filter(user=request.user)
    return render(request, 'cats/index.html', {'cats': cats})
@login_required
def cat_detail(request, cat_id):
    cat = Cat.objects.get(id=cat_id)
    # toys = Toy.objects.all()
    toys_cat_doesnt_have = Toy.objects.exclude(id__in = cat.toys.all().values_list("id"))
    # instantiate FeedingForm to be rendered in the template
    feeding_form = FeedingForm()
    return render(request, 'cats/detail.html', {'cat': cat, 'feeding_form': feeding_form, 'toys': toys_cat_doesnt_have})
class CatCreate(CreateView, LoginRequiredMixin):
    model = Cat
    fields = ['name', 'breed', 'description', 'age']
    # This inherited method is called when a valid cat form is being submitted
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user  # form.instance is the cat
        # Let the CreateView do its job as usual
        return super().form_valid(form)
class CatUpdate(UpdateView, LoginRequiredMixin):
    model = Cat
    # Let's disallow the renaming of a cat by excluding the name field!
    fields = ['breed', 'description', 'age']
class CatDelete(DeleteView, LoginRequiredMixin):
    model = Cat
    success_url = '/cats/'
@login_required
def add_feeding(request, cat_id):
    # create a ModelForm instance using the data in request.POST
    form = FeedingForm(request.POST)
    # validate the form
    if form.is_valid():
        # don't save the form to the db until it
        # has the cat_id assigned
        new_feeding = form.save(commit=False)
        new_feeding.cat_id = cat_id
        new_feeding.save()
    return redirect('cat_detail', cat_id=cat_id)
class ToyCreate(CreateView, LoginRequiredMixin):
    model = Toy
    fields = '__all__'
class ToyList(ListView, LoginRequiredMixin):
    model = Toy
class ToyDetail(DetailView, LoginRequiredMixin):
    model = Toy
class ToyUpdate(UpdateView, LoginRequiredMixin):
    model = Toy
    fields = ['name', 'color']
class ToyDelete(DeleteView, LoginRequiredMixin):
    model = Toy
    success_url = '/toys/'
@login_required
def associate_toy(request, cat_id, toy_id):
    # Note that you can pass a toy's id instead of the whole object
    Cat.objects.get(id=cat_id).toys.add(toy_id)
    return redirect('cat_detail', cat_id=cat_id)
@login_required
def remove_toy(request, cat_id, toy_id):
    Cat.objects.get(id=cat_id).toys.remove(toy_id)
    return redirect('cat_detail', cat_id=cat_id)
def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in
            login(request, user)
            return redirect('cat_index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)
        # Same as: return render(request, 'signup.html', {'form': form, 'error_message': error_message})