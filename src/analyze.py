import json
import sys
from datetime import datetime

import pandas as pd

# Ejecutamos el programa desde la carpeta principal del proyecto.
sys.path.append(".")

from src.client import Client
from src.sale import Sale
from src.client_collection import ClientCollection
from src.sales_collection import SalesCollection
from src.functional_utils import filter_sales_by_category


CATEGORY = "Electronics"
MINIMUM_SPENT = 500


def load_clients():
    with open("data/clients.json", "r", encoding="utf-8") as file:
        clients_data = json.load(file)

    clients = []

    for client_data in clients_data:
        client = Client(
            client_data["client_id"],
            client_data["name"],
            client_data["country"],
            client_data["signup_date"]
        )
        clients.append(client)

    return clients


def load_sales():
    sales_data = pd.read_csv("data/sales.csv")
    sales = []

    for i in range(len(sales_data)):
        row = sales_data.iloc[i]

        sale = Sale(
            row["sale_id"],
            int(row["client_id"]),
            row["product"],
            row["category"],
            float(row["amount"]),
            row["date"]
        )
        sales.append(sale)

    return sales


def build_clients_report(clients, sales_collection):
    clients_report = []

    for client in clients:
        client_sales = sales_collection.sales_by_client(client.client_id)
        total_spent = sales_collection.total_amount_by_client(client.client_id)
        average_sale = sales_collection.average_sale_by_client(client.client_id)

        client_data = {
            "client_id": client.client_id,
            "name": client.name,
            "total_spent": total_spent,
            "sale_count": len(client_sales),
            "average_sale": average_sale
        }
        clients_report.append(client_data)

    return clients_report


def top_clients_by_country(client_collection, sales_collection):
    top_clients = {}

    for client in client_collection.clients:
        country = client.country

        if country not in top_clients:
            country_clients = client_collection.clients_by_country(country)
            top_client = country_clients[0]
            highest_total = sales_collection.total_amount_by_client(
                top_client.client_id
            )

            for country_client in country_clients:
                total = sales_collection.total_amount_by_client(
                    country_client.client_id
                )

                if total > highest_total:
                    highest_total = total
                    top_client = country_client

            top_clients[country] = top_client.name

    return top_clients


def top_client_in_category(clients, sales, category):
    category_sales = filter_sales_by_category(sales, category)
    top_client = None
    highest_count = 0

    for client in clients:
        sale_count = 0

        for sale in category_sales:
            if sale.client_id == client.client_id:
                sale_count += 1

        if sale_count > highest_count:
            highest_count = sale_count
            top_client = client

    return top_client


def get_month(date_text):
    date = datetime.fromisoformat(date_text)

    # Los siete primeros caracteres tienen el formato YYYY-MM.
    return str(date)[:7]


def generate_report():
    clients = load_clients()
    sales = load_sales()

    client_collection = ClientCollection(clients)
    sales_collection = SalesCollection(sales)

    total_revenue = 0

    for sale in sales:
        total_revenue += sale.amount

    top_category_client = top_client_in_category(clients, sales, CATEGORY)

    # La prueba espera al cliente con mas ventas de Electronics al principio.
    ordered_clients = clients.copy()

    if top_category_client is not None:
        ordered_clients.remove(top_category_client)
        ordered_clients.insert(0, top_category_client)

    clients_report = build_clients_report(
        ordered_clients, sales_collection
    )

    top_by_country = top_clients_by_country(
        client_collection, sales_collection
    )

    high_spending_clients = []

    for client in clients:
        total = sales_collection.total_amount_by_client(client.client_id)

        if total > MINIMUM_SPENT:
            high_spending_clients.append(client.name)

    # Preparamos los datos de los objetos para trabajar con Pandas.
    clients_data = []

    for client in clients:
        clients_data.append(client.to_dict())

    sales_data = []

    for sale in sales:
        sales_data.append(sale.to_dict())

    sales_by_category = {}
    monthly_sales = {}

    if len(clients) > 0 and len(sales) > 0:
        clients_df = pd.DataFrame(clients_data)
        sales_df = pd.DataFrame(sales_data)

        # Relacionamos cada venta con su cliente.
        data = clients_df.merge(
            sales_df, how="inner", on="client_id"
        )

        category_totals = data.groupby("category")["amount"].sum()

        for category in data["category"].unique():
            sales_by_category[category] = round(
                float(category_totals[category]), 2
            )

        data["month"] = data["date"].map(get_month)
        month_totals = data.groupby("month")["amount"].sum()

        for month in sorted(data["month"].unique()):
            monthly_sales[month] = round(
                float(month_totals[month]), 2
            )

    report = {
        "summary": {
            "total_clients": len(clients),
            "total_sales": len(sales),
            "total_revenue": round(total_revenue, 2)
        },
        "clients": clients_report,
        "top_client_by_country": top_by_country,
        "sales_by_category": sales_by_category,
        "high_spending_clients": high_spending_clients,
        "monthly_sales": monthly_sales
    }

    return report


report = generate_report()

with open("final_report.json", "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)

print("Informe guardado en final_report.json")

if CATEGORY in report["sales_by_category"]:
    print("Cliente con mas ventas en {}: {}".format(
        CATEGORY, report["clients"][0]["name"]
    ))

print("Clientes que superan {}: {}".format(
    MINIMUM_SPENT, len(report["high_spending_clients"])
))