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
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .. import settings

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


class UserProfileView(JSONResponseMixin, generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):

        response_dict = {
            "user_registration": "profile_created"
        }

        if not user_profile_exists(request):
            try:
                userprofile = UserProfile(user_id=Users.objects.get(email_address=request.user.email), about_me="Default about me",
                                            address=request.data.get("address"), city=request.data.get("city"), state=request.data.get("state"),
                                            postal_code="576200", phone_primary=request.data.get("phone_primary"))

                # TODO:  IMPLEMENT UPDATE, NOT JUST SAVE PROFILE.
                userprofile.save()

                if (get_user_registration_status(request) != "registered"):
                    user = Users.objects.get(user_id=Users.objects.get(email_address=request.user.email).user_id)
                    user.registration_status=RegistrationStatus.objects.get(status="registered")
                    user.save()

            except:
                response_dict = {
                    "user_registration": "profile_creation_failed"
                }
                raise
        else:
            # User profile exists. So, you must update it.
            response_dict = {
                "user_registration": "update_succeeded"
            }

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
class MeasuringUnitView(viewsets.ModelViewSet):
    queryset = MeasuringUnit.objects.all()
    serializer_class = MeasuringUnitSerializer


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


class MyListingsView(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializerNew

    def get_queryset(self):
        seller = Seller.objects.get(seller=Users.objects.get(name=self.request.user))
        queryset = Inventory.objects.filter(seller=seller)
        return queryset


class InventoryView(JSONResponseMixin, generics.ListCreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventoryItemSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @csrf_exempt
    def post(self, request):
        try:

            inventory_item = Inventory()
            inventory_item.listing_title = request.data.get("listing_title")
            inventory_item.inventory_item_status = InventoryItemStatus.objects.get(pk=2)
            inventory_item.product = get_product(product_name=request.data.get("product_name"))
            inventory_item.inventory_product_quantity = request.data.get("quantity")
            inventory_item.seller = get_seller(request)
            inventory_item.product_measuring_unit = get_product_measuring_unit(request.data.get("measuring_unit"))

            item_picture = handle_uploaded_file(file=request.FILES["image"], seller=inventory_item.seller)

            if item_picture == "error":
                raise Exception

            inventory_item.item_picture = item_picture
            inventory_item.item_price = request.data.get("price")
            inventory_item.product_category = get_product_category(
                category=inventory_item.product.product_category.category_id)

            inventory_item.save()
            return self.render_json_response({"inventory_id": inventory_item.pk})
        except:
            traceback.print_exc()
            return self.render_json_response({"inventory_update": "failed"})


class InventoryItemView(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventoryItemSerializerNew
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        unformatted = Inventory.objects.filter(inventory_item_id=self.kwargs["pk"])
        return unformatted

    def post(self, request, **kwargs):
        return False
        # Update is not supported.
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance, self.request.data)

        return self.render_json_response({"status": "updated"})

    def delete(self, request, *args, **kwargs):
        print("Delete was requested by user {}".format (request.user))
        seller = get_seller(request)
        inventory_item = self.get_queryset()
        print(inventory_item)
        if len(inventory_item) > 0:
            if str(inventory_item[0].seller.seller.name) == str(request.user):
                self.get_queryset().delete()
                delete_listing_image(filename=inventory_item[0].item_picture)

                return self.render_json_response({"response": "deleted"})
            else:
                return self.render_json_response({"response": "permission_denied"})
        else:
            return self.render_json_response({"response": "No such listing!"})


# each inventory item can have its own address. Default is sellers address.
class InventoryItemAddressView(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = InventoryItemAddress.objects.all()
    serializer_class = InventoryItemAddressSerializer


# transporters have an id, their transportation capacity, and what they're willing to transport.
class TransporterView(viewsets.ModelViewSet):
    queryset = Transporter.objects.all()
    serializer_class = TransporterSerializer


class VehicleView(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer


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

    def is_registration_complete(self, request):
        try:
            user_object = Users.objects.get(email_address=request.user.email,
                                            registration_status=RegistrationStatus.objects.get(pk=1))
            # If there is no exception, then, the given user's registration_status 2 == registered.
            # So, return True.
            return True
        except ObjectDoesNotExist:
            return False

    def register_user(self, registration_data, auth_token):
        pass

    def add_new_user(self, request):

        # On first login, the user is in unverified status (4); and his registration_status is unregistered(2)
        new_user = Users(user_status=UserStatus.objects.get(pk=2), name=request.user.username,
                         email_address=request.user.email, registration_status=RegistrationStatus.objects.get(pk=2))

        if self.oauth_provider == "google":
            new_user.google_user_id = self.oauth_provided_user_id

        if self.oauth_provider == "facebook":
            new_user.fb_user_id = self.oauth_provided_user_id

        new_user.save()

    def send_email_verification_code(self, request):
        pass

    def send_phone_verification_code(selfs, request):
        pass

    def do_email_verification(self, request):
        pass

    def do_phone_verification(self, request):
        pass

    def is_email_verified(self, request):
        verification_status = False
        try:
            verification_status = UserProfile.objects.get(id=Users.objects.get(email_address=request.user.email),
                                                          email_verified="false")
            verification_status = True
        except:
            pass

        return verification_status

    def is_phone_verified(self, request):
        verification_status = False
        try:
            verification_status = UserProfile.objects.get(id=Users.objects.get(email_address=request.user.email),
                                                          phone_verified="false")
            verification_status = True
        except:
            pass

        return verification_status

    def post(self, request, *args, **kwargs):

        if self.is_new_user(request):
            registration_pending = True
            # Create an entry in Users table.
            self.add_new_user(request)
        else:
            if self.is_registration_complete(request):
                registration_pending = False
            else:
                registration_pending = True

        return self.render_json_response({"registration_pending": registration_pending})


class IsRegisteredUser(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    @csrf_exempt
    def post(self, request):
        is_registration_complete = UserAuth().is_registration_complete(request)
        return self.render_json_response({"registered": is_registration_complete})


class ListingsByCategory(generics.ListAPIView):
    serializer_class = InventoryItemSerializerNew

    def __init__(self):
        self.response = {
            "listings": None,
            "errors": None
        }

    def get_queryset(self):
        print(self.request.query_params)
        category_id = get_product_category(category=self.kwargs["category"])
        queryset = Inventory.objects.filter(product_category=category_id)
        return queryset


class ListingsByProduct(JSONResponseMixin, CsrfExemptMixin, APIView):
    pass


class ListingsByUser(JSONResponseMixin, CsrfExemptMixin, APIView):
    pass


class SearchListings(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    def do_search(self, request):
        # Could this be a free-text search? User can type-in anything.
        pass


class IsSeller(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    def post(self, request):
        if is_seller(request):
            return self.render_json_response({"seller": True})
        else:
            return self.render_json_response({"seller": False})


class RegisterAsSeller(JSONResponseMixin, CsrfExemptMixin, APIView):
    def __init__(self):
        pass

    def post(self, request):
        if is_seller(request):
            return self.render_json_response({"response": "already_registered"})
        else:
            user_id = get_user(request)
            try:
                seller = Seller(seller=user_id).save()
                return self.render_json_response({"response": "success"})
            except:
                return self.render_json_response({"response": "failed"})


class TextTemplateView(viewsets.ModelViewSet, APIView):
    queryset = TextTemplate.objects.all()
    serializer_class = TextTemplateSerializer


class NegotiationRequestStatusView(viewsets.ModelViewSet):
    queryset = NegotiationRequestStatus.objects.all()
    serializer_class = NegotiationRequestStatusSerializer


class NegotiationRequestActionsView(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = NegotiationRequest.objects.all()
    serializer_class  = NegotiationRequestSerializer

    def partial_update(self, request, **kwargs):
        seller = get_seller(request)
        if request.data.get("accepted"):
            instance = self.get_object()
            negotiation_request_status = NegotiationRequestStatus.objects.get(status="accepted")
            instance.accepted = negotiation_request_status
            instance.save()
            return self.render_json_response({"response": "success"})

        if request.data.get("rejected"):
            print("rejecting.")
            instance = self.get_object()
            negotiation_request_status = NegotiationRequestStatus.objects.get(status="rejected")
            instance.accepted = negotiation_request_status
            instance.save()
            return self.render_json_response({"response": "success"})


class NegotiationRequestView(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = NegotiationRequest.objects.all()
    serializer_class = NegotiationRequestSerializer

    @csrf_exempt
    def post(self, request, **kwargs):
        print(request.data.get("listing_id"))
        listing_id = request.data.get("listing_id")
        listing_instance = get_inventory_item_instance(listing_id=listing_id)
        buyer = get_request_as_buyer(request)
        listing_details = get_listing_details(listing_id=listing_id)
        sent_by = "buyer"
        request_body = "Hello, lets do business." if request.data.get("request_body") =="" or \
        request.data.get("request_body") == "undefined" else request.data.get("request_body")

        seller = get_seller_of_listing(listing_id=listing_id)

        # Check the need for inserting a new record.
        try:
            existing_record = NegotiationRequest.objects.get(
                Q(listing_id=listing_id),
                Q(buyer=buyer)
            )
            print("existing record")
            if existing_record.listing_id:
                return self.render_json_response({"response": "failed", "reason": "You've contacted this seller already."})
        except:
            # We should keep going if the record doesn't exist.
            pass

        negotiation_request = NegotiationRequest()
        negotiation_request.listing_id = listing_instance
        negotiation_request.buyer = buyer
        negotiation_request.request_body = request_body
        negotiation_request.seller = seller
        negotiation_request.accepted = NegotiationRequestStatus.objects.get(
            status_id=settings.NEGOTIATION_REQUEST_STATUS.get("pending"))

        negotiation_request.sent_by = sent_by
        print("{} {} {} {} {}".format(listing_id, buyer, sent_by, request_body, seller))
        try:
            negotiation_request.save()
            return self.render_json_response({"response": negotiation_request.pk})
        except:

            return self.render_json_response({"response": "failed"})

    def update(self, request, **kwargs):
        return self.render_json_response({"response": "put"})

    def partial_update(self, request, **kwargs):
        pass


class MeNegotiationRequestSent(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = NegotiationRequest.objects.all()
    serializer_class = MyNegotiationRequestsSerializer

    def get_queryset(self):
        try:
            requesting_user = get_user_id_by_name(username=self.request.user)
            buyer = get_user_as_buyer(requesting_user)
            negotiation_requests = NegotiationRequest.objects.filter(
                Q(buyer=buyer)
            )
            
            print(negotiation_requests)

            return negotiation_requests
        except:
            # We should keep going if the record doesn't exist.
            pass


class MeNegotiationRequestReceived(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = NegotiationRequest.objects.all()
    serializer_class = MyNegotiationRequestsSerializerReceived

    def get_queryset(self):
        try:
            requesting_user_id = get_user_id_by_name(username=self.request.user)
            seller = get_seller_from_id(user_id=requesting_user_id)
            negotiation_requests_received = NegotiationRequest.objects.filter(
                Q(seller=seller)
            )

            return negotiation_requests_received
        except:
            raise
            # We should keep going if the record doesn't exist.
            pass


class PlaygroundView(JSONResponseMixin, viewsets.ModelViewSet):
    queryset = NegotiationRequest.objects.all()
    serializer_class = MyNegotiationRequestsSerializer

    def get_queryset(self):
        try:
            requesting_user_id = get_user_id_by_name(username=self.request.user)
            seller = get_seller_from_id(user_id=requesting_user_id)
            negotiation_requests = NegotiationRequest.objects.filter(
                Q(seller=seller)
            )
            if not negotiation_requests:
                return self.render_json_response({"response": "failed", "listings": "[]"})

            return negotiation_requests
        except:
            # We should keep going if the record doesn't exist.
            pass
