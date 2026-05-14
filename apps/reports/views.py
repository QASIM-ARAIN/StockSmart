from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from apps.products.models import Product
from apps.transactions.models import Transaction

@login_required
def reports_view(request):
    # Summary stats
    total_products = Product.objects.count()
    low_stock_products = [p for p in Product.objects.all() if p.is_low_stock()]
    low_stock_count = len(low_stock_products)

    total_stock_in = sum(
        t.quantity for t in Transaction.objects.filter(transaction_type='IN')
    )
    total_stock_out = sum(
        t.quantity for t in Transaction.objects.filter(transaction_type='OUT')
    )

    # Top 10 products by current stock
    top_products = Product.objects.order_by('-current_stock')[:10]
    top_product_names = [p.name for p in top_products]
    top_product_stocks = [p.current_stock for p in top_products]

    # Transactions over last 7 days
    last_7_days = []
    stock_in_data = []
    stock_out_data = []

    for i in range(6, -1, -1):
        day = timezone.now().date() - timedelta(days=i)
        last_7_days.append(day.strftime('%d %b'))
        stock_in_data.append(
            sum(t.quantity for t in Transaction.objects.filter(
                transaction_type='IN',
                date__date=day
            ))
        )
        stock_out_data.append(
            sum(t.quantity for t in Transaction.objects.filter(
                transaction_type='OUT',
                date__date=day
            ))
        )

    return render(request, 'reports/reports.html', {
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'total_stock_in': total_stock_in,
        'total_stock_out': total_stock_out,
        'low_stock_products': low_stock_products,
        'top_product_names': top_product_names,
        'top_product_stocks': top_product_stocks,
        'last_7_days': last_7_days,
        'stock_in_data': stock_in_data,
        'stock_out_data': stock_out_data,
    })