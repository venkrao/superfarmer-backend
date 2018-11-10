from .serializer import *
from .models import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from braces.views import CsrfExemptMixin, JSONResponseMixin
from django.conf import settings
import requests
from django.core.exceptions import ObjectDoesNotExist


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
        print("request user " + request.user)
        try:
            # TODO: IMPLEMENT is_token_valid()
            userprofile = UserProfile(user_id=Users.objects.get(user_id=request.data.get("user_id")), about_me="",
                                        address=request.data.get("address"), city=request.data.get("city"), state=request.data.get("state"),
                                        postal_code="576200", phone_primary=request.data.get("phone_primary"))

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
class ProductCategoryView(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


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


# a list of all advertised products.
class InventoryView(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer


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

    def is_new_user(self):
        try:
            user_object = Users.objects.get(email_address=self.email)
            self.user_id = user_object.user_id
            return False
        except ObjectDoesNotExist:
            return True

    def register_user(self, registration_data, auth_token):
        pass

    def add_new_user(self, request):
        print("request user :" + request.user)
        new_user = Users(user_status=UserStatus.objects.get(pk=2), name=self.name, email_address=self.email,
                         registration_status=RegistrationStatus.objects.get(pk=2))

        if self.oauth_provider == "google":
            new_user.google_user_id = self.oauth_provided_user_id

        if self.oauth_provider == "facebook":
            new_user.fb_user_id = self.oauth_provided_user_id

        new_user.save()

    def post(self, request, *args, **kwargs):
        social_auth_userdata = request.data.get("social_auth_userdata")
        if social_auth_userdata:
            token = social_auth_userdata.get("token")

            self.oauth_provider = social_auth_userdata.get("token_provider")

            self.name = token.get("name")
            self.email = token.get("email")
            self.image = token.get("image")
            self.oauth_provided_user_id = token.get("id")
            self.provider = token.get("provider")
            self.oauth_provider_token = token.get("token")

            # convert the social auth token into drf token - self.convert_token
            self.converted_token = self.convert_token()

            # check if the user is new user. - self.is_new_user()
            if self.is_new_user():
                registration_pending = True
                # Create an entry in Users table.
                self.add_new_user(request)
            else:
                registration_pending = False

            response_dict = {
                "converted_token": self.converted_token,
                "user_id": self.user_id,
                "registration_pending": registration_pending
            }
            # If registration_pending, then, frontend will force the user to register, and
            # send registration data to backend, handled by register_user()
            return self.render_json_response(context_dict=response_dict)

        # if not, register the user - self.register_user()
        registration_data = request.data.get("registration_data")
        if registration_data:
            auth_token = request.data.get("auth_token")
            if not auth_token:
                return self.render_json_response({"user_registration": "unauthorized_request"})

            if self.register_user(registration_data, auth_token):
                status = "succeeded"
            else:
                status = "failed"

            return self.render_json_response({"user_registration": status})

from django.views.decorators.csrf import csrf_exempt

class PlaygroundView(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    @csrf_exempt
    def post(self, request):
        print(request.user)
        return self.render_json_response({"HELLO": "request"})


