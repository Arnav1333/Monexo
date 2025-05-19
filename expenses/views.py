from django.shortcuts import render,redirect,get_object_or_404
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm
from .models import Expense

# Create your views here.

def home(request):
    return render(request,'base.html')

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'dashboard.html', {'expenses': expenses})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'edit_expense.html', {'form': form})

@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
        return redirect('dashboard')
    return render(request, 'delete_expense.html', {'expense': expense})

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration_done.html' , {'new_user': new_user})
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})



@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('dashboard')  # or any page you'd like
    else:
        form = ExpenseForm()
    return render(request, 'add_expense.html', {'form': form})