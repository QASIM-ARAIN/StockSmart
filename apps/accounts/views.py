from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.factory import UserFactory
from apps.accounts.models import User

def home_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.status == 'pending':
                messages.warning(request, 'Your account is pending admin approval.')
            elif user.status == 'rejected':
                messages.error(request, 'Your registration was rejected. Contact the administrator.')
            else:
                login(request, user)
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'All fields are required.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            if role == 'admin':
                UserFactory.create_admin(username, password, email)
                messages.success(request, 'Admin account created. You can now log in.')
            else:
                UserFactory.create_staff(username, password, email)
                messages.success(request, 'Registration submitted. Please wait for admin approval.')
            return redirect('login')

    return render(request, 'accounts/register.html')

@login_required
def dashboard_view(request):
    from apps.products.models import Product
    from apps.transactions.models import Transaction

    total_products = Product.objects.count()
    low_stock_products = [p for p in Product.objects.all() if p.is_low_stock()]
    low_stock_count = len(low_stock_products)
    total_transactions = Transaction.objects.count()
    total_users = User.objects.filter(status='active').count()
    recent_transactions = Transaction.objects.order_by('-date')[:5]
    pending_users = User.objects.filter(status='pending').count()

    return render(request, 'accounts/dashboard.html', {
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'total_transactions': total_transactions,
        'total_users': total_users,
        'recent_transactions': recent_transactions,
        'pending_users': pending_users,
    })

@login_required
def user_list_view(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')

    users = User.objects.all().order_by('status', 'username')
    pending_users = User.objects.filter(status='pending').count()
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'pending_users': pending_users
    })

@login_required
def approve_user_view(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)
    user.status = 'active'
    user.save()
    messages.success(request, f'{user.username} has been approved.')
    return redirect('user_list')

@login_required
def reject_user_view(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')

    user = get_object_or_404(User, pk=pk)
    user.status = 'rejected'
    user.save()
    messages.warning(request, f'{user.username} has been rejected.')
    return redirect('user_list')