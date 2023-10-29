from django.shortcuts import render, redirect
from bmstu_lab.models import *
import psycopg2
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from rest_framework.decorators import api_view
from datetime import datetime
from django.db.models import Q





class CurrentUserSingleton: 
    _instance = None 
 
    @classmethod 
    def get_instance(cls): 
        if not cls._instance: 
            cls._instance = cls._get_user() 
        return cls._instance 
 
    @classmethod 
    def _get_user(cls): 
        return Users.objects.get(user_id=1, user_name='user', is_admin=False)


@api_view(['GET'])
def GetProductss(request, format=None):
    """
    Возвращает список объектов
    """
    print('get')
    product = Products.objects.all()
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def GetProductsById(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = get_object_or_404(Products, pk=pk)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)


@api_view(['POST'])
def PostProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def PostProductToApplication(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    try: 
        application = Application.objects.filter(id_user=current_user, status="Зарегистрирован").latest('creation_date')
    except:
        application = Application(
            status='Зарегистрирован',
            creation_date=datetime.now(),
            user_id=current_user,
        )
        application.save()
    application_id = application
    try:
        product = Products.objects.get(pk=pk, status='enabled')
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)
    try:
        application_product = ApplicationProducts.objects.get(application_id=application_id, product_id=product)
        return Response("Такой рецепт уже добавлен в заявку")
    except ApplicationProducts.DoesNotExist:
        application_product = ApplicationProducts(
            application_id=application_id,
            product_id=product,
        )
        application_product.save()
    application_subscription = ApplicationProducts.objects.filter(application_id = application_id)
    serializer = ApplicationProductstSerializer(application_product, many=True)
    # applications = Application.objects.all()
    # serializer = ApplicationSerializer(applications, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def putProducts(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = get_object_or_404(Products, pk=pk)
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def deleteProduct(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = Products.objects.get(pk=pk)
    product.status = "deleted"
    product.save()

    product = Products.objects.filter(status="enabled")
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def getApplications(request):
    date_format = "%Y-%m-%d"
    start_date_str = request.query_params.get('start', '2023-01-01')
    end_date_str = request.query_params.get('end', '2023-12-31')
    start = datetime.strptime(start_date_str, date_format).date()
    end = datetime.strptime(end_date_str, date_format).date()
    
    status = request.data.get('status')

    applications = Application.objects.filter(
        ~Q(status="Удалено"),
        creation_date__range=(start, end)
    )
    
    if status:
        applications = applications.filter(status=status)

    applications = applications.order_by('creation_date')
    serializer = ApplicationSerializer(applications, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
def getApplication(request, pk):
    try:
        application = Application.ofbjects.get(pk=pk)
        if application.status == "Удалено" or not application:
            return Response("Заявки с таким id нет")

        application_serializer = ApplicationSerializer(application)
        application_products = ApplicationProducts.objects.filter(application_id=application)
        application_products_serializer = ApplicationProductstSerializer(application_products, many=True)

        response_data = {
            'application': application_serializer.data,
            'products': application_products_serializer.data
        }

        return Response(response_data)
    except Application.DoesNotExist:
        return Response("Заявки с таким id нет")


@api_view(['DELETE'])
def deleteApplication(request, pk):
    if not Application.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id нет")
    application = Application.objects.get(pk=pk)
    application.status = "Удалено"
    application.save()

    application = Application.objects.all()
    serializer = ApplicationSerializer(application, many=True)
    return Response(serializer.data)


@api_view(['PUT']) 
def putApplication(request, pk):
    try:
        order = Application.objects.get(pk=pk)
    except Application.DoesNotExist:
        return Response("Заявки с таким id нет")
    serializer = ApplicationSerializer(order, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(serializer.errors)
    serializer.save()

    order = Application.objects.all()
    serializer = ApplicationSerializer(order, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def putApplicationByAdmin(request, pk):
    if not Application.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id нет")
    application = Application.objects.get(pk=pk)
    if application.status != "Проверяется":
        return Response("Такой заявки нет на проверке")
    if request.data["status"] not in ["Отказано", "Принято"]:
        return Response("Неверный статус!")
    application.status = request.data["status"]
    application.publication_date=datetime.now().date()
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)


@api_view(['PUT'])
def putApplicationByUser(request):
    current_user = CurrentUserSingleton.get_instance()
    try:
        application = get_object_or_404(Application, user_id=current_user, status="Зарегистрирован")
    except:
        return Response("Такой заявки нет")
    
    application.status = "Проверяется"
    application.processed_at=datetime.now().date()
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)



@api_view(['PUT'])
def PutApplicationProduct(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    application = get_object_or_404(Application, id_user=current_user, status="Зарегистрирован")
    
    try:
        product = Products.objects.get(pk=pk, status='enabled')
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)
    
    application_product = ApplicationProducts.objects.filter(id_application=application, product_id=product).first()
    if application_product:
        product_id = request.data.get('product_id')
        try:
            product = Products.objects.get(id=product_id, status='enabled')
            application_product.product_id = product
            application_product.save()
            serializer = ApplicationProductstSerializer(application_product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
        except Products.DoesNotExist:
            return Response("Такого продукта нет", status=400)
    else:
        return Response("Заявка не найдена", status=404)
    

@api_view(['DELETE'])
def DeleteApplicationProduct(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    application = get_object_or_404(Application, id_user=current_user, status="Зарегистрирован")
    try:
        product = Products.objects.get(pk=pk, status='enabled')
        try:
            application_product = get_object_or_404(ApplicationProducts, id_application=application, id_subscription=product)
            application_product.delete()
            return Response("Продукт удален", status=200)
            # application_product = ApplicationProducts.objects.all()
            # serializer = ApplicationProductstSerializer(application_product, many=True)
            # return Response(serializer.data)
        except ApplicationProducts.DoesNotExist:
            return Response("Заявка не найдена", status=404)
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)





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



