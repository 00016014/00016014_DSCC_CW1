from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Task, Category, Tag
from .forms import TaskForm, CategoryForm


# Task management views - CRUD operations

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')
    return render(request, 'core/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    tasks = Task.objects.filter(author=request.user)
    total = tasks.count()
    done = tasks.filter(status='done').count()
    in_progress = tasks.filter(status='in_progress').count()
    todo = tasks.filter(status='todo').count()
    recent = tasks[:3]
    progress_percent = round((done / total) * 100) if total > 0 else 0
    return render(request, 'core/dashboard.html', {
        'total': total,
        'done': done,
        'in_progress': in_progress,
        'todo': todo,
        'recent': recent,
        'progress_percent': progress_percent,
    })


@login_required
def task_list(request):
    tasks = Task.objects.filter(author=request.user)
    category_filter = request.GET.get('category')
    priority_filter = request.GET.get('priority')
    status_filter = request.GET.get('status')
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'core/task_list.html', {
        'tasks': tasks,
        'categories': categories,
        'selected_category': category_filter,
        'selected_priority': priority_filter,
        'selected_status': status_filter,
    })


@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, author=request.user)
    return render(request, 'core/task_detail.html', {'task': task})


@login_required
def task_create(request):
    form = TaskForm(request.user, request.POST or None)
    if form.is_valid():
        task = form.save(commit=False)
        task.author = request.user
        task.save()
        form.save_m2m()
        return redirect('task_list')
    return render(request, 'core/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk, author=request.user)
    form = TaskForm(request.user, request.POST or None, instance=task)
    if form.is_valid():
        form.save()
        return redirect('task_detail', pk=task.pk)
    return render(request, 'core/task_form.html', {'form': form, 'action': 'Edit'})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, author=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('task_list')
    return render(request, 'core/task_confirm_delete.html', {'task': task})


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        cat = form.save(commit=False)
        cat.user = request.user
        cat.save()
        return redirect('category_list')
    cats_with_counts = []
    for cat in categories:
        cats_with_counts.append({
            'obj': cat,
            'count': Task.objects.filter(author=request.user, category=cat).count()
        })
    return render(request, 'core/category_list.html', {
        'cats_with_counts': cats_with_counts,
        'form': form,
    })


@login_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        cat.delete()
    return redirect('category_list')