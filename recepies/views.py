from django.shortcuts import render, redirect
from recepies.models import *
import psycopg2
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .serializers import *
from rest_framework.decorators import api_view
from datetime import datetime
from django.db.models import Q
from minio import Minio
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework import viewsets
from .permissions import *
from django.conf import settings
import redis
import uuid
from django.contrib.sessions.models import Session

session_storage = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class CurrentUserSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls._get_user()
        return cls._instance

    @classmethod
    def _get_user(cls):
        return CustomUser.objects.get(
            email="check@list.ru",
            password="pbkdf2_sha256$600000$XjFy1vVc2KoGlNI6tDpWVb$r7ahJQyjwhRmtacF8Td2+FubN6Ny3wLwuqgnvqT6kYg=",
        )


@api_view(["GET"])
def GetProducts(request, format=None):
    # print("get")
    # product = Products.objects.all()
    # serializer = ProductSerializer(product, many=True)
    # return Response(serializer.data)
    products = Products.objects.filter(status="enabled")

    # if product_name:
    #     products = products.filter(title__icontains=product_name)
    try:
        ssid = request.COOKIES["session_id"]
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
        product = Products.objects.filter(
            id_user=current_user, status="Зарегистрирован"
        ).latest("creation_date")
        serializer = ProductSerializer(products, many=True)
        application_serializer = ProductSerializer(application)
        result = {
            "application_id": application_serializer.data["id"],
            "products": serializer.data,
        }
        return Response(result)
    except:
        serializer = ProductSerializer(products, many=True)
        result = {"products": serializer.data}
        return Response(result)


@api_view(["GET"])
def GetProductsById(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = get_object_or_404(Products, pk=pk)
    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)


# @swagger_auto_schema(method="post", request_body=ProductSerializer)
@api_view(["POST"])
@permission_classes([IsManager])
def PostProduct(request):
    data = request.data.copy()  # Создаем копию данных запроса
    data["status"] = "enabled"  # Устанавливаем значение "enabled" для поля "status"

    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        new_option = serializer.save()
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,
        )
        i = new_option.id - 1
        try:
            i = new_option.product_name
            img_obj_name = f"{i}.jpeg"
            file_path = f"photos/{request.data.get('photo')}"
            client.fput_object(
                bucket_name="products", object_name=img_obj_name, file_path=file_path
            )
            new_option.photo = f"minio://localhost:9000/products/{img_obj_name}"
            new_option.save()
        # try:
        #     i = new_option.id
        #     img_obj_name = f"{i}.jpg"
        #     file_path = f"assets/{request.data.get('src')}"
        #     client.fput_object(bucket_name='images',
        #                     object_name=img_obj_name)
        #                     # file_path=file_path)
        #     new_option.src = f"localhost:9000/images/{img_obj_name}"
        #     new_option.save()
        except Exception as e:
            return Response({"error": str(e)})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @swagger_auto_schema(method="post", request_body=ProductSerializer)
@api_view(["POST"])
@permission_classes([IsAuth])
def PostProductToApplication(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    try:
        application = Application.objects.filter(
            id_user=current_user, status="Зарегистрирован"
        ).latest("creation_date")
    except:
        application = Application(
            status="Зарегистрирован",
            creation_date=datetime.now(),
            user_id=current_user,
        )
        application.save()
    application_id = application
    try:
        product = Products.objects.get(pk=pk, status="enabled")
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)
    try:
        application_product = ApplicationProducts.objects.get(
            application_id=application_id, product_id=product
        )
        return Response("Такой рецепт уже добавлен в заявку")
    except ApplicationProducts.DoesNotExist:
        application_product = ApplicationProducts(
            application_id=application_id,
            product_id=product,
        )
        application_product.save()
    # application_subscription = ApplicationProducts.objects.filter(
    #     application_id=application_id
    # )
    # serializer = ApplicationProductstSerializer(application_product, many=True)
    # # applications = Application.objects.all()
    # # serializer = ApplicationSerializer(applications, many=True)
    # return Response(serializer.data)

    addedProduct = Products.objects.get(pk=pk)
    serializer = SubscriptionSerializer(addedProduct)
    return Response(serializer.data)


# @swagger_auto_schema(method="put", request_body=ProductSerializer)
@api_view(["PUT"])
@permission_classes([IsManager])
def putProducts(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = get_object_or_404(Products, pk=pk)
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsManager])
def deleteProduct(request, pk):
    if not Products.objects.filter(pk=pk).exists():
        return Response(f"Продукта с таким id нет")
    product = Products.objects.get(pk=pk)
    product.status = "deleted"
    product.save()

    product = Products.objects.filter(status="enabled")
    serializer = ProductSerializer(product, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuth])
def getApplications(request):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    date_format = "%Y-%m-%d"
    start_date_str = request.query_params.get("start", "2023-01-01")
    end_date_str = request.query_params.get("end", "2023-12-31")
    start = datetime.strptime(start_date_str, date_format).date()
    end = datetime.strptime(end_date_str, date_format).date()

    status = request.data.get("status")

    if current_user.is_superuser:  # Модератор может смотреть заявки всех пользователей
        print("модератор")
        applications = Application.objects.filter(
            ~Q(status="Удалено"), creation_date__range=(start, end)
        )
    else:  # Авторизованный пользователь может смотреть только свои заявки
        print("user")
        applications = Application.objects.filter(
            ~Q(status="Удалено"),
            id_user=current_user.id,
            creation_date__range=(start, end),
        )

    if status:
        applications = applications.filter(status=status)

    applications = applications.order_by("creation_date")
    serializer = ApplicationSerializer(applications, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuth])
def getApplication(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    try:
        application = Application.objects.get(pk=pk)
        if application.status == "Удалено" or not application:
            return Response("Заявки с таким id нет")
        application_serializer = ApplicationSerializer(application)

        if (
            not current_user.is_superuser
            and current_user.id == application_serializer.data["id_user"]
        ) or (current_user.is_superuser):
            application_products = ApplicationProducts.objects.filter(
                application=application
            )
            product_ids = [product.id for product in application_products]
            print(product_ids)
            products_queryset = Products.objects.filter(id__in=product_ids)
            products_serializer = ProductSerializer(products_queryset, many=True)
            response_data = {
                "application": application_serializer.data,
                "product": products_serializer.data,
            }
            return Response(response_data)
        else:
            return Response("Заявки с таким id нет")
        # application_products = ApplicationProducts.objects.filter(
        #     application_id=application
        # )
        # application_products_serializer = ApplicationProductstSerializer(
        #     application_products, many=True
        # )

        # response_data = {
        #     "application": application_serializer.data,
        #     "products": application_products_serializer.data,
        # }

        # return Response(response_data)
    except Application.DoesNotExist:
        return Response("Заявки с таким id нет")


@api_view(["DELETE"])
@permission_classes([IsAuth])
def deleteApplication(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    try:
        application = Application.objects.get(
            id_user=current_user, status="Зарегистрирован"
        )
        application.status = "Удалено"
        application.save()
        return Response({"status": "Success"})
    except:
        return Response("У данного пользователя нет заявки", status=400)
    # if not Application.objects.filter(pk=pk).exists():
    #     return Response(f"Заявки с таким id нет")
    # application = Application.objects.get(pk=pk)
    # application.status = "Удалено"
    # application.save()

    # application = Application.objects.all()
    # serializer = ApplicationSerializer(application, many=True)
    # return Response(serializer.data)


# @swagger_auto_schema(method="put", request_body=ApplicationSerializer)
@api_view(["PUT"])
@permission_classes([IsManager])
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


# @swagger_auto_schema(method="put", request_body=ApplicationSerializer)
@api_view(["PUT"])
@permission_classes([IsManager])
def putApplicationByAdmin(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    if not Application.objects.filter(pk=pk).exists():
        return Response(f"Заявки с таким id нет")
    application = Application.objects.get(pk=pk)
    if application.status != "Проверяется":
        return Response("Такой заявки нет на проверке")
    if request.data["status"] not in ["Отказано", "Принято"]:
        return Response("Неверный статус!")
    application.status = request.data["status"]
    application.publication_date = datetime.now().date()
    application.id_moderator = current_user
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)


# @swagger_auto_schema(method="put", request_body=ApplicationSerializer)
@api_view(["PUT"])
def putApplicationByUser(request):
    current_user = CurrentUserSingleton.get_instance()
    try:
        application = get_object_or_404(
            Application, user_id=current_user, status="Зарегистрирован"
        )
    except:
        return Response("Такой заявки нет")

    application.status = "Проверяется"
    application.processed_at = datetime.now().date()
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)


# @swagger_auto_schema(method="put", request_body=ApplicationProductstSerializer)
@api_view(["PUT"])
def PutApplicationProduct(request, pk):
    current_user = CurrentUserSingleton.get_instance()
    application = get_object_or_404(
        Application, id_user=current_user, status="Зарегистрирован"
    )

    try:
        product = Products.objects.get(pk=pk, status="enabled")
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)

    application_product = ApplicationProducts.objects.filter(
        id_application=application, product_id=product
    ).first()
    if application_product:
        product_id = request.data.get("product_id")
        try:
            product = Products.objects.get(id=product_id, status="enabled")
            application_product.product_id = product
            application_product.save()
            serializer = ApplicationProductstSerializer(
                application_product, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=400)
        except Products.DoesNotExist:
            return Response("Такого продукта нет", status=400)
    else:
        return Response("Заявка не найдена", status=404)


@api_view(["PUT"])
@permission_classes([IsAuth])
def sendApplication(request):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")

    try:
        application = get_object_or_404(
            Application, id_user=current_user, status="Зарегистрирован"
        )
    except:
        return Response("Такой заявки не зарегистрировано")

    application.status = "Проверяется"
    application.publication_date = datetime.now().date()
    application.save()
    serializer = ApplicationSerializer(application)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuth])
def DeleteApplicationProduct(request, pk):
    ssid = request.COOKIES["session_id"]
    try:
        email = session_storage.get(ssid).decode("utf-8")
        current_user = CustomUser.objects.get(email=email)
    except:
        return Response("Сессия не найдена")
    application = get_object_or_404(
        Application, id_user=current_user, status="Зарегистрирован"
    )
    # try:
    #     product = Products.objects.get(pk=pk, status="enabled")
    #     try:
    #         application_product = get_object_or_404(
    #             ApplicationProducts, id_application=application, id_subscription=product
    #         )
    #         application_product.delete()
    try:
        product = Products.objects.get(pk=pk, status="enabled")
        application_from_product = ApplicationProducts.objects.filter(
            application=application
        )
        try:
            application_product = get_object_or_404(
                ApplicationProducts, application=application, products=product
            )
            application_product.delete()
            if len(application_from_product) == 0:
                application = get_object_or_404(
                    Application, id_user=current_user, status="Зарегистрирован"
                )
                application.status = "Удалено"
                application.save()
            return Response("Продукт удален", status=200)

        except ApplicationProducts.DoesNotExist:
            return Response("Заявка не найдена", status=404)
    except Products.DoesNotExist:
        return Response("Такого продукта нет", status=400)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer
#     model_class = CustomUser

#     def create(self, request):
#         if self.model_class.objects.filter(email=request.data["email"]).exists():
#             return Response({"status": "Exist"}, status=400)
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             print(serializer.data)
#             self.model_class.objects.create_user(
#                 email=serializer.data["email"],
#                 password=serializer.data["password"],
#                 is_superuser=serializer.data["is_superuser"],
#                 is_staff=serializer.data["is_staff"],
#             )
#             return Response({"status": "Success"}, status=200)
#         return Response(
#             {"status": "Error", "error": serializer.errors},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# @permission_classes([AllowAny])
# @authentication_classes([])
# @csrf_exempt
# @swagger_auto_schema(method="post", request_body=UserSerializer)
# @api_view(["Post"])
# def login_view(request):
#     email = request.POST["email"]  # допустим передали username и password
#     password = request.POST["password"]
#     user = authenticate(request, email=email, password=password)
#     if user is not None:
#         login(request, user)
#         return HttpResponse("{'status': 'ok'}")
#     else:
#         return HttpResponse("{'status': 'error', 'error': 'login failed'}")


# def logout_view(request):
#     logout(request._request)
#     return Response({"status": "Success"})


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    model_class = CustomUser
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request):
        print("req is", request.data)
        if self.model_class.objects.filter(email=request.data["email"]).exists():
            return Response({"status": "Exist"}, status=400)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            self.model_class.objects.create_user(
                email=serializer.data["email"],
                password=serializer.data["password"],
                # full_name=serializer.data["full_name"],
                # phone_number=serializer.data["phone_number"],
                is_superuser=serializer.data["is_superuser"],
                is_staff=serializer.data["is_staff"],
            )
            random_key = str(uuid.uuid4())
            session_storage.set(random_key, serializer.data["email"])
            user_data = {
                "email": request.data["email"],
                # "full_name": request.data["full_name"],
                # "phone_number": request.data["phone_number"],
                "is_superuser": False,
            }

            print("user data is ", user_data)
            response = Response(user_data, status=status.HTTP_201_CREATED)
            # response = HttpResponse("{'status': 'ok'}")
            response.set_cookie("session_id", random_key)
            return response
            # return Response({'status': 'Success'}, status=200)
        return Response(
            {"status": "Error", "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


@swagger_auto_schema(method="post", request_body=UserSerializer)
@api_view(["Post"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("email")
    password = request.data.get("password")
    user = authenticate(request, email=username, password=password)

    if user is not None:
        print(user)
        random_key = str(uuid.uuid4())
        session_storage.set(random_key, username)
        user_data = {
            "id": user.id,
            "email": user.email,
            # "full_name": user.full_name,
            # "phone_number": user.phone_number,
            "password": user.password,
            "is_superuser": user.is_superuser,
        }
        response = Response(user_data, status=status.HTTP_201_CREATED)
        response.set_cookie(
            "session_id", random_key, samesite="Lax", max_age=30 * 24 * 60 * 60
        )
        return response
    else:
        return HttpResponse("login failed", status=400)


@api_view(["POST"])
@permission_classes([IsAuth])
def logout_view(request):
    ssid = request.COOKIES["session_id"]
    if session_storage.exists(ssid):
        session_storage.delete(ssid)
        response_data = {"status": "Success"}
    else:
        response_data = {"status": "Error", "message": "Session does not exist"}
    return Response(response_data)


@api_view(["GET"])
# @permission_classes([IsAuth])
def user_info(request):
    try:
        ssid = request.COOKIES["session_id"]
        if session_storage.exists(ssid):
            email = session_storage.get(ssid).decode("utf-8")
            user = CustomUser.objects.get(email=email)
            user_data = {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "is_superuser": user.is_superuser,
            }
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Error", "message": "Session does not exist"})
    except:
        return Response({"status": "Error", "message": "Cookies are not transmitted"})
