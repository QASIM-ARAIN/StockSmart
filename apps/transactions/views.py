from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.transactions.models import Transaction
from apps.products.models import Product, Supplier
from apps.transactions.factory import TransactionFactory

@login_required
def transaction_list(request):
    transaction_type = request.GET.get('type')
    product_id = request.GET.get('product')

    transactions = Transaction.objects.all().order_by('-date')

    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    if product_id:
        transactions = transactions.filter(product_id=product_id)

    products = Product.objects.all()
    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'products': products,
        'selected_type': transaction_type,
        'selected_product': product_id,
    })

@login_required
def stock_in(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        supplier_id = request.POST.get('supplier')
        notes = request.POST.get('notes')

        if not product_id or not quantity:
            messages.error(request, 'Product and quantity are required.')
        elif int(quantity) <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
        else:
            product = get_object_or_404(Product, pk=product_id)
            supplier = Supplier.objects.filter(pk=supplier_id).first() if supplier_id else None
            TransactionFactory.create_stock_in(
                product=product,
                quantity=int(quantity),
                user=request.user,
                supplier=supplier,
                notes=notes
            )
            messages.success(request, f'Stock in recorded for {product.name}.')
            return redirect('transaction_list')

    products = Product.objects.all()
    suppliers = Supplier.objects.all()
    return render(request, 'transactions/stock_in.html', {
        'products': products,
        'suppliers': suppliers
    })

@login_required
def stock_out(request):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        quantity = request.POST.get('quantity')
        out_reason = request.POST.get('out_reason')
        notes = request.POST.get('notes')

        if not product_id or not quantity:
            messages.error(request, 'Product and quantity are required.')
        elif int(quantity) <= 0:
            messages.error(request, 'Quantity must be greater than zero.')
        else:
            product = get_object_or_404(Product, pk=product_id)
            try:
                TransactionFactory.create_stock_out(
                    product=product,
                    quantity=int(quantity),
                    user=request.user,
                    out_reason=out_reason,
                    notes=notes
                )
                messages.success(request, f'Stock out recorded for {product.name}.')
                return redirect('transaction_list')
            except ValueError as e:
                messages.error(request, str(e))

    products = Product.objects.all()
    return render(request, 'transactions/stock_out.html', {'products': products})