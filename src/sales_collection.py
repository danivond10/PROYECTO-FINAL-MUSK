class SalesCollection:
    def __init__(self, sales):
        self.sales = sales

    def sales_by_client(self, client_id):
        sales_found = []

        for sale in self.sales:
            if sale.client_id == client_id:
                sales_found.append(sale)

        return sales_found

    def total_amount_by_client(self, client_id):
        total = 0
        client_sales = self.sales_by_client(client_id)

        for sale in client_sales:
            total += sale.amount

        return total

    def total_amount_by_category(self, category):
        total = 0

        for sale in self.sales:
            if sale.category == category:
                total += sale.amount

        return total

    def average_sale_by_client(self, client_id):
        client_sales = self.sales_by_client(client_id)
        sale_count = len(client_sales)

        # Evita dividir entre cero cuando el cliente no tiene ventas.
        if sale_count == 0:
            return 0

        total = self.total_amount_by_client(client_id)
        return round(total / sale_count, 2)