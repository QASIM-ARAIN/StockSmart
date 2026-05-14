from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.products.models import Product, Category, Supplier
@login_required
def product_list(request):
    category_id = request.GET.get('category')
    search = request.GET.get('search', '')
    
    products = Product.objects.all()
    
    if category_id:
        products = products.filter(category_id=category_id)
    if search:
        products = products.filter(name__icontains=search)
    
    categories = Category.objects.all()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search': search
    })

@login_required
def product_add(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        unit = request.POST.get('unit')
        minimum_threshold = request.POST.get('minimum_threshold')
        current_stock = request.POST.get('current_stock')

        if not name or not unit or not minimum_threshold or not current_stock:
            messages.error(request, 'All fields are required')
        else:
            product = Product.objects.create(
                name=name,
                category_id=category_id if category_id else None,
                unit=unit,
                minimum_threshold=int(minimum_threshold),
                current_stock=0,
                created_by=request.user
            )
            # Record initial stock as Stock In transaction
            initial_stock = int(current_stock)
            if initial_stock > 0:
                from apps.transactions.factory import TransactionFactory
                TransactionFactory.create_stock_in(
                product=product,
                quantity=initial_stock,
                 user=request.user,
                 supplier=None,
                 notes='Initial Stock'
                  )
            messages.success(request, f'Product "{name}" added successfully')
            return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'products/product_form.html', {
        'categories': categories,
        'action': 'Add'
    })

@login_required
def product_edit(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')

    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        unit = request.POST.get('unit')
        minimum_threshold = request.POST.get('minimum_threshold')

        if not name or not unit or not minimum_threshold:
            messages.error(request, 'All fields are required')
        else:
            product.name = name
            product.category_id = category_id if category_id else None
            product.unit = unit
            product.minimum_threshold = int(minimum_threshold)
            product.save()
            messages.success(request, f'Product "{name}" updated successfully')
            return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'products/product_form.html', {
        'product': product,
        'categories': categories,
        'action': 'Edit'
    })

@login_required
def product_delete(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')
    
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully')
        return redirect('product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def category_list(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')
    
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})

@login_required
def category_add(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if not name:
            messages.error(request, 'Category name is required')
        elif Category.objects.filter(name=name).exists():
            messages.error(request, 'Category already exists')
        else:
            Category.objects.create(name=name)
            messages.success(request, f'Category "{name}" added successfully')
            return redirect('category_list')
    
    return render(request, 'products/category_form.html')


from apps.products.models import Product, Category, Supplier

@login_required
def supplier_list(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')
    suppliers = Supplier.objects.all().order_by('name')
    return render(request, 'products/supplier_list.html', {'suppliers': suppliers})

@login_required
def supplier_add(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        contact_person = request.POST.get('contact_person')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')

        if not name:
            messages.error(request, 'Supplier name is required.')
        else:
            Supplier.objects.create(
                name=name,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address
            )
            messages.success(request, f'Supplier "{name}" added successfully.')
            return redirect('supplier_list')

    return render(request, 'products/supplier_form.html')

@login_required
def supplier_edit(request, pk):
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admins only.')
        return redirect('product_list')

    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        supplier.name = request.POST.get('name')
        supplier.contact_person = request.POST.get('contact_person')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.address = request.POST.get('address')
        supplier.save()
        messages.success(request, f'Supplier updated successfully.')
        return redirect('supplier_list')

    return render(request, 'products/supplier_form.html', {'supplier': supplier})

@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    transactions = product.transaction_set.all().order_by('-date')
    total_in = sum(t.quantity for t in transactions if t.transaction_type == 'IN')
    total_out = sum(t.quantity for t in transactions if t.transaction_type == 'OUT')
    return render(request, 'products/product_detail.html', {
        'product': product,
        'transactions': transactions,
        'total_in': total_in,
        'total_out': total_out,
    })