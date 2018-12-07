from .serializer import *
from .models import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from braces.views import CsrfExemptMixin, JSONResponseMixin
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from .util import *
import traceback
from django.http import HttpResponse, JsonResponse
from rest_framework.generics import RetrieveAPIView
from rest_framework_serializer_extensions.views import SerializerExtensionsAPIViewMixin
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

class UsersView(viewsets.GenericViewSet):
    def get(self, request):

        pass


class UserCategoryView(viewsets.ModelViewSet, APIView):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer



class UserStatusView(viewsets.ModelViewSet, APIView):
    queryset = UserStatus.objects.all()
    serializer_class = UserStatusSerializer


class UsersView(viewsets.ModelViewSet, APIView):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


class UserProfileView(CsrfExemptMixin, JSONResponseMixin, APIView):
    def __init__(self):
        pass

    def post(self, request, *args, **kwargs):

        try:

            userprofile = UserProfile(user_id=Users.objects.get(email_address=request.user.email), about_me="Default about me",
                                        address=request.data.get("address"), city=request.data.get("city"), state=request.data.get("state"),
                                        postal_code="576200", phone_primary=request.data.get("phone_primary"))

            # TODO:  IMPLEMENT UPDATE, NOT JUST SAVE PROFILE.
            userprofile.save()

            response_dict = {
                "user_registration": "success"
            }
        except:
            response_dict = {
                "user_registration": "failed"
            }
            raise

        return self.render_json_response(context_dict=response_dict)


# List of categories the web portal is supporting.
class ProductCategoryView(viewsets.ModelViewSet, viewsets.ViewSet, generics.ListAPIView):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('category_name', 'category_id')


# a product has an id, and it belongs to a category.
class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


# each product has a measuring unit, a base measuring unit and a multiplier.
# measuring unit = multiplier * base measuring unit
class ProductMeasuringUnitView(viewsets.ModelViewSet):
    queryset = ProductMeasuringUnit.objects.all()
    serializer_class = ProductMeasuringUnitSerializer


# list of sellers, with the list of products they sell.
class SellerView(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer


# list of buyers, with the list of products they buy.
class BuyerView(viewsets.ModelViewSet):
    queryset = Buyer.objects.all()
    serializer_class = BuyerSerializer

# inventory item has a status: draft, active, suspended, unavailable.
class InventoryItemStatusView(viewsets.ModelViewSet):
    queryset = InventoryItemStatus.objects.all()
    serializer_class = InventoryItemStatusSerializer


class InventoryView(JSONResponseMixin, generics.ListCreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryItemSerializer

    @csrf_exempt
    def post(self, request):
        try:
            print(request.FILES["image"])
            item_picture = handle_uploaded_file(request.FILES["image"])
            print(item_picture)
            if item_picture == "error":
                raise Exception

            inventory_item = Inventory()

            inventory_item.inventory_item_status = InventoryItemStatus.objects.get(pk=2)
            inventory_item.product = get_product(product_name=request.data.get("product_name"))
            inventory_item.inventory_product_quantity = request.data.get("quantity")
            inventory_item.seller = get_seller(request)
            inventory_item.product_measuring_unit = get_product_measuring_unit(request.data.get("measuring_unit"))
            inventory_item.item_picture = item_picture
            inventory_item.product_category = get_product_category(
                category=1)  # TODO: THIS SHOULD BE READ OUT OF THE REQUEST.

            inventory_item.save()
            return self.render_json_response({"inventory_id": inventory_item.pk})
        except:
            traceback.print_exc()
            return self.render_json_response({"inventory_update": "failed"})


class InventoryItemView(SerializerExtensionsAPIViewMixin, JSONResponseMixin, generics.ListAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryItemSerializer

    def get_queryset(self):
        unformatted = Inventory.objects.filter(inventory_item_id=self.kwargs["pk"])
        return unformatted


# each inventory item can have its own address. Default is sellers address.
class InventoryItemAddressView(viewsets.ModelViewSet):
    queryset = InventoryItemAddress.objects.all()
    serializer_class = InventoryItemAddressSerializer


# transporters have an id, their transportation capacity, and what they're willing to transport.
class TransporterView(viewsets.ModelViewSet):
    queryset = Transporter.objects.all()
    serializer_class = TransporterSerializer


class RegistrationStatusView(viewsets.ModelViewSet):
    queryset = RegistrationStatus.objects.all()
    serializer_class = RegistrationStatusSerializer


class UserAuth(CsrfExemptMixin, JSONResponseMixin, APIView):

    def __init__(self):
        self.converted_token = None
        self.name = None
        self.email = None
        self.image = None
        self.id = None
        self.provider = None
        self.oauth_provider_token = None
        self.oauth_provider = None
        self.user_id = 00000000

    def is_new_user(self, request):
        try:
            user_object = Users.objects.get(email_address=request.user.email)
            self.user_id = user_object.user_id
            return False
        except ObjectDoesNotExist:
            return True

    def is_registration_pending(self, request):
        try:
            user_object = Users.objects.get(email_address=request.user.email,
                                            registration_status=RegistrationStatus.objects.get(pk=2))
            # If there is no exception, then, the given user's registration_status is still 2 == pending.
            # So, return True.
            return True
        except ObjectDoesNotExist:
            return False


    def register_user(self, registration_data, auth_token):
        pass

    def add_new_user(self, request):
        print(request.user)
        # On first login, the user is in unverified status (4); and his registration_status is unregistered(2)
        new_user = Users(user_status=UserStatus.objects.get(pk=2), name=request.user.username, email_address=request.user.email,
                         registration_status=RegistrationStatus.objects.get(pk=2))

        if self.oauth_provider == "google":
            new_user.google_user_id = self.oauth_provided_user_id

        if self.oauth_provider == "facebook":
            new_user.fb_user_id = self.oauth_provided_user_id

        new_user.save()

    def post(self, request, *args, **kwargs):

        if self.is_new_user(request):
            registration_pending = True
            # Create an entry in Users table.
            self.add_new_user(request)
        else:
            if self.is_registration_pending(request):
                registration_pending = True
            else:
                registration_pending = False

        return self.render_json_response({"registration_pending": registration_pending})



class PlaygroundView(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    @csrf_exempt
    def post(self, request):
        print(request.user)
        return self.render_json_response({"HELLO": "request"})


