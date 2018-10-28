from .serializer import *
from .models import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from braces.views import CsrfExemptMixin, JSONResponseMixin
from django.conf import settings

class UserCategoryView(viewsets.ModelViewSet):
    queryset = UserCategory.objects.all()
    serializer_class = UserCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class UserStatusView(viewsets.ModelViewSet):
    queryset = UserStatus.objects.all()
    serializer_class = UserStatusSerializer

class UsersView(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer


class UserContactInfoView(viewsets.ModelViewSet):
    queryset = UserContactInfo.objects.all()
    serializer_class = UserContactInfoSerializer


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


class UserAuth(CsrfExemptMixin, JSONResponseMixin, APIView):

    def __init__(self):
        self.converted_token = None
        self.name = None
        self.email = None
        self.image = None
        self.id = None
        self.provider = None

    def convert_token(self, social_auth_userdata):
        pass

    def is_new_user(self):
        if self.provider == "google":
            if Users.objects.get(google_user_id=self.id):
                return False
        if self.provider == "facebook":
            if Users.objects.get(fb_user_id=self.id):
                return False

        return True


    def register_user(self, registration_data, auth_token):
        pass

    def post(self, request, *args, **kwargs):
        social_auth_userdata = request.POST.get("social_auth_userdata")
        if social_auth_userdata:
            self.name = social_auth_userdata.name
            self.email = social_auth_userdata.email
            self.image = social_auth_userdata.image
            self.id = social_auth_userdata.id
            self.provider = social_auth_userdata.provider

            # convert the social auth token into drf token - self.convert_token
            self.converted_token = self.convert_token(social_auth_userdata)

            # check if the user is new user. - self.is_new_user()
            if self.is_new_user():
                registration_pending = True
            else:
                registration_pending = False

                response_dict = {
                    "converted_token": self.converted_token,
                    "registration_pending": registration_pending
                }
                # If registration_pending, then, frontend will force the user to register, and
                # send registration data to backend, handled by register_user()
                return self.render_json_response(context_dict=response_dict)

        # if not, register the user - self.register_user()
        registration_data = request.POST.get("registration_data")
        if registration_data:
            auth_token = request.POST.get("auth_token")
            if not auth_token:
                return self.render_json_response({"user_registration": "unauthorized_request"})

            if self.register_user(registration_data, auth_token):
                status = "succeeded"
            else:
                status = "failed"

            return self.render_json_response({"user_registration": status})
