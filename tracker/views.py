from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.http import HttpResponse
from datetime import date
from .models import Expense, Category
from .forms import ExpenseForm
import csv

# ---------- Auth Views ----------

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password)

        send_mail(
            subject='Welcome to Expenzo 🎉',
            message=f'Hi {username},\n\nThank you for signing up for Expenzo!\nStart managing your expenses smarter today.',
            from_email='kingkalam956@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Account created successfully.")
        return redirect('login')

    return render(request, 'tracker/signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect('main_page')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'tracker/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

# ---------- Main Pages ----------

def homepage(request):
    return render(request, 'tracker/home.html') 

def main_page_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tracker/main_page.html', {'username': request.user.username})


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'tracker/dashboard.html')

# ---------- Expenses ----------

def add_expense(request):
    if not request.user.is_authenticated:
        return redirect('login')
    form = ExpenseForm(request.POST or None)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        expense.save()
        messages.success(request, "Expense added.")
        return redirect('add_expense')
    return render(request, 'tracker/add_expense.html', {'form': form})


def view_expenses(request):
    if not request.user.is_authenticated:
        return redirect('login')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.all()

    q = request.GET.get('q')
    cat = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if q:
        expenses = expenses.filter(title__icontains=q)
    if cat:
        expenses = expenses.filter(category__name=cat)
    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)

    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tracker/view_expenses.html', {
        'expenses': page_obj,
        'categories': categories,
        'page_obj': page_obj
    })


def edit_expense(request, expense_id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        expense = Expense.objects.get(id=expense_id, user=request.user)
    except Expense.DoesNotExist:
        messages.error(request, "Expense not found.")
        return redirect('view_expenses')

    form = ExpenseForm(request.POST or None, instance=expense)
    if form.is_valid():
        form.save()
        messages.success(request, "Expense updated.")
        return redirect('view_expenses')

    return render(request, 'tracker/edit_expense.html', {'form': form})


def delete_expense(request, expense_id):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        expense = Expense.objects.get(id=expense_id, user=request.user)
        expense.delete()
        messages.success(request, "Expense deleted.")
    except Expense.DoesNotExist:
        messages.error(request, "Expense not found.")
    return redirect('view_expenses')

# ---------- Categories ----------

def add_category_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, "Category already exists.")
        else:
            Category.objects.create(name=name)
            messages.success(request, "Category added.")
            return redirect('main_page')
    return render(request, 'tracker/add_category.html')

# ---------- Summary ----------

def summary_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    expenses = Expense.objects.filter(user=request.user)

    total_all = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    today = date.today()
    total_today = expenses.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    total_month = expenses.filter(date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    category_totals = expenses.values('category__name').annotate(total=Sum('amount'))

    return render(request, 'tracker/summary.html', {
        'total_all': total_all,
        'total_today': total_today,
        'total_month': total_month,
        'category_totals': category_totals,
    })

# ---------- CSV Export ----------

def export_expenses_csv(request):
    if not request.user.is_authenticated:
        return redirect('login')
    expenses = Expense.objects.filter(user=request.user).order_by('-date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Amount', 'Category', 'Date', 'Note'])

    for e in expenses:
        writer.writerow([e.title, e.amount, e.category.name if e.category else '', e.date, e.note])

    return response

# ---------- Profile ----------

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password and new_password == confirm_password:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Password updated successfully.")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'tracker/profile.html', {'user': request.user})

# ---------- Admin Dashboard ----------

def admin_dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if not request.user.is_staff:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('main_page')

    total_users = User.objects.count()
    total_expenses = Expense.objects.count()
    total_amount = Expense.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    users = User.objects.all().order_by('id')

    return render(request, 'tracker/admin_dashboard.html', {
        'total_users': total_users,
        'total_expenses': total_expenses,
        'total_amount': total_amount,
        'users': users,
    })
