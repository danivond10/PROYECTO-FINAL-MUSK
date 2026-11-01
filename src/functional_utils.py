def filter_sales_by_category(sales, category):
    filtered_sales = []

    for sale in sales:
        if sale.category == category:
            filtered_sales.append(sale)

    return filtered_sales


def filter_sales_by_date(sales, date):
    filtered_sales = []

    for sale in sales:
        if sale.date == date:
            filtered_sales.append(sale)

    return filtered_sales