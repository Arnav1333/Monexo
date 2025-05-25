from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegistrationForm, ExpenseForm
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncMonth, TruncDate
from datetime import datetime, timedelta
from django.utils import timezone
import json
from decimal import Decimal

# Create your views here.

def home(request):
    return render(request,'base.html')

@login_required

def dashboard(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    
   
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get monthly expenses
    monthly_expenses = expenses.filter(
        date__month=current_month,
        date__year=current_year
    )
    
    # Calculate analytics data
    total_monthly = monthly_expenses.aggregate(total=Sum('amount'))['total'] 
    
    # Get weekly expenses (last 7 days)
    week_ago = current_date - timedelta(days=7)
    weekly_expenses = expenses.filter(date__gte=week_ago)
    total_weekly = weekly_expenses.aggregate(total=Sum('amount'))['total'] 
    
    # Get category breakdown
    category_breakdown = expenses.values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Calculate average expense
    avg_expense = expenses.aggregate(avg=Avg('amount'))['avg'] or Decimal('0')
    
    # Get highest expense
    highest_expense = expenses.order_by('-amount').first()
    highest_amount = highest_expense.amount if highest_expense else Decimal('0')
    
    # Most used category
    top_category = category_breakdown.first() if category_breakdown else None
    
    # Prepare context with analytics data
    context = {
        'expenses': expenses[:50],  # Limit to latest 50 for performance
        'total_monthly': total_monthly,
        'total_weekly': total_weekly,
        'avg_expense': avg_expense,
        'highest_amount': highest_amount,
        'top_category': top_category,
        'category_breakdown': category_breakdown,
        'expenses_count': expenses.count(),
        
        # For JavaScript processing - all expenses data
        'all_expenses': expenses,
    }
    
    return render(request, 'dashboard.html', context)


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