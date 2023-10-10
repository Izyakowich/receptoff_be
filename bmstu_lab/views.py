from django.shortcuts import render, redirect
from datetime import date
from bmstu_lab.models import *
import psycopg2

# def GetData():
#     return [
#         {
#             "title": "Морковь",
#             "id": 1,
#             "img": "https://cdnn21.img.ria.ru/images/07e5/06/08/1736135954_0:188:3072:1916_1920x0_80_0_0_d0264c42d6166d2821602edf39fab775.jpg",
#             "cathegory": "овощи",
#             "taste": "сладкая",
#         },
#         {
#             "title": "Картофель",
#             "id": 2,
#             "img": "https://resizer.mail.ru/p/65d821e4-5978-5fd0-90d4-b93e85001e86/AAAcuIW20M8UJ0DLAVxajNbJxXVLPVCxum64542hjFrUTS9iAK8l2EuwSOCFMiyTPSdW373rdjoFcEw4KHvCt-Dr2Pc.jpg",
#             "cathegory": "овощи",
#             "taste": "твердая",
#         },
#         {
#             "title": "Лук",
#             "id": 3,
#             "img": "https://storum.ru/image/cache/products/152768-800x800.jpeg",
#             "cathegory": "овощи",
#             "taste": "вкусный, но заставляет плакать",
#         },
#         {
#             "title": "Огурец",
#             "id": 4,
#             "img": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQZf4rcv6JJ30fMuDcbu0Ta9yCcor8ABLQu_Q&usqp=CAU",
#             "cathegory": "овощи",
#             "taste": "мокрый, любят попугаи",
#         },
#     ]


# def GetProducts(request):
#     query = request.GET.get("sub")
#     print(query)
#     subs = GetData()
#     res = []

#     if query is None:
#         return render(
#             request, "products.html", {"data": {"products": GetData(), "query_c": ""}}
#         )
#     else:
#         for sub in subs:
#             if query is not None:
#                 if query.lower() in sub["title"].lower():
#                     res.append(sub)
#             else:
#                 res = subs

#     return render(
#         request, "products.html", {"data": {"products": res, "query_c": query}}
#     )


# def GetProduct(request, id):
#     productsData = GetData()
#     product = next((sub for sub in productsData if sub["id"] == id), None)
#     if product:
#         print(product["cathegory"])
#     else:
#         print("Not found")
#     return render(request, "product.html", {"data": {"product": product}})


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
