from django.shortcuts import render, redirect
from datetime import date
from bmstu_lab.models import *
import psycopg2



def GetProducts(request):
    data = Products.objects.filter(status="enabled").values()
    query = request.GET.get("sub")
    query = "" if query == None else query
    print("text:", query)
    if query != "":
        data = Products.objects.filter(
            product_name=query.lower()
        ) & Products.objects.filter(status="enabled")
        return render(request, "products.html", {"products": data, "query_c": query})
    return render(request, "products.html", {"products": data, "query_c": ""})


def GetProduct(request, id):
    product = Products.objects.get(product_id=id)
    print(product)
    return render(request, "product.html", {"data": product})


def DeleteProduct(request):
    if request.method == "POST":
        product_id = request.POST.get("delete")
        print("id", product_id)
        ChangeStatus(product_id)
        data = Products.objects.filter(status="enabled").values()
        return render(request, "products.html", {"products": data})


def ChangeStatus(id):
    conn = psycopg2.connect(
        dbname="recepies",
        host="localhost",
        user="postgres",
        password="1234567890",
        port="5432",
    )
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET status = 'deleted' WHERE product_id=%s",
        (id),
    )
    conn.commit()
    cursor.close()
    conn.close()
