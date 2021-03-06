from .models import *
from rest_framework import serializers

from rest_framework.serializers import ModelSerializer
from rest_framework_serializer_extensions.serializers import SerializerExtensionsMixin
from collections import OrderedDict
from .util import *
from django.db.models import Q
from rest_framework.fields import CurrentUserDefault

class UserCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCategory
        fields = '__all__'


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'


class UsersSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = ('user_status', 'registration_status')


class UserNameSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('name',)


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        sanitized = sanitize_user_address(ret)

        return sanitized


class UserProfileSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        depth = 3

    def validate(self, data):
        pass

    def update(self, instance, validated_data):
        pass

    def to_representation(self, instance):

        ret = super().to_representation(instance)

        try:
            otp = PhoneOTP.objects.get(user_id=ret.get("user_id")["user_id"])
            otp = {"exists": True, "phone_number": otp.phone_number}
        except:
            otp = {"exists": False}
            print("OTP not generated yet.")

        ret["otp"] = otp

        return ret


# List of categories the web portal is supporting.
class ProductCategorySerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('category_name', )


# a product has an id, and it belongs to a category.
class ProductSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('product_name', 'product_category', 'product_default_image')

        expandable_fields = dict(
            product_category=dict(
                serializer=ProductCategorySerializer,
                id_source='product_category.pk'
            ),
        )


# each product has a measuring unit, a base measuring unit and a multiplier.
# measuring unit = multiplier * base measuring unit
class MeasuringUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasuringUnit
        exclude = ('measuring_unit_id',)


class ProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name']


# list of sellers, with the list of products they sell.
class SellerNameSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
        class Meta:
            model = Seller
            fields = ('seller',)

            expandable_fields = dict(
                seller=dict(
                    serializer=UserNameSerializer,
                    id_source='seller.pk'),
            )


# list of sellers, with the list of products they sell.
class SellerSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

        expandable_fields = dict(
            seller=dict(
            serializer=UsersSerializer,
            id_source='seller.pk'),
        )


# list of buyers, with the list of products they buy.
class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'


# inventory item has a status: draft, active, suspended, unavailable.
class InventoryItemStatusSerializer(SerializerExtensionsMixin, serializers.ModelSerializer):
    class Meta:
        model = InventoryItemStatus
        fields = ('status', )


class InventoryItemSerializerNew(ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        depth = 6

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        sellerInstance = ret.get("seller")
        user_id = sellerInstance.get("seller").get("user_id")
        userProfile = UserProfileSerializer(UserProfile.objects.get(user_id=user_id)).data

        address = get_inventory_item_address(item_id=ret.get("inventory_item_id"))

        if address == None:
            address = userProfile
        else:
            address = InventoryItemAddressSerializer(address).data
            address["phone_primary"] = userProfile.get("phone_primary")
            address["phone_verified"] = userProfile.get("phone_verified", "false")
            address["email_verified"] = userProfile.get("email_verified", "false")

        ret.update(address=address)

        seller_user_id = sellerInstance.get("seller").get("user_id")
        requesting_user = get_user_id_by_name(username=self.context['request'].user)
        if (requesting_user):
            if requesting_user == seller_user_id:
                print("seller is self")
                ret.update(soldby="self")
            else:
                print("current user is not the seller")
                try:
                    buyer = get_user_as_buyer(requesting_user)
                    existing_record = NegotiationRequest.objects.get(
                        Q(listing_id=ret.get("inventory_item_id")),
                        Q(buyer=buyer)
                    )
                    print("existing record")
                    if existing_record.listing_id:
                        ret.update(soldby="already_contacted")
                except:
                    # We should keep going if the record doesn't exist.
                    ret.update(soldby="real_seller")
        else:
            ret.update(soldby="user_not_loggedin")

        sanitized = sanitize_inventory_item(ret)

        return sanitized

    def validate_listing_title(self, value):
        if value == "":
            raise serializers.ValidationError("listing title is required.")

        return value

    def validate_item_price(self, value):
        if value == "":
            raise serializers.ValidationError("item price is required.")

        return value


    def update(self, instance, validated_data):
        save = False

        if validated_data.get("listing_title") != "":
            save = True
            instance.listing_title = validated_data.get("listing_title")

        if validated_data.get("item_price") != "":
            save = True
            instance.item_price = validated_data.get("item_price")

        if validated_data.get("inventory_product_quantity") != "":
            save = True
            instance.inventory_product_quantity = validated_data.get("inventory_product_quantity")

        if validated_data.get("item_price") != "":
            save = True
            instance.item_price = validated_data.get("item_price")

        """
        if validated_data.get("inventory_available_from_datetime") != "":
            save = True
            instance.inventory_available_from_datetime = validated_data.get("inventory_available_from_datetime")
        """

        if validated_data.get("item_picture") != "":
            save = True
            instance.item_picture = validated_data.get("item_picture")

        if save == True:
            instance.save()

    def is_valid(self, raise_exception=True):
        return False


class MyListingsSerializer(ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        depth = 6

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        address = get_inventory_item_address(item_id=ret.get("inventory_item_id"))
        if address == None:
            sellerInstance = ret.get("seller")

            user_id = sellerInstance.get("seller").get("user_id")
            address = UserProfileSerializer(UserProfile.objects.get(user_id=user_id)).data

        ret.update(address=address)
        sanitized = sanitize_inventory_item(ret)

        return sanitized


# a list of all advertised products.
class InventoryItemSerializer(SerializerExtensionsMixin, ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'
        depth = 6

    def to_representation(self, instance):
        sanitized = {}
        try:
            ret = super().to_representation(instance)
            sellerInstance = ret.get("seller")
            seller_user_id = sellerInstance.get("seller").get("user_id")
            requesting_user = get_user_id_by_name(username=self.context['request'].user)
            if (requesting_user):
                if requesting_user == seller_user_id:
                    print("seller is self")
                    ret.update(soldby="self")
                else:
                    print("current user is not the seller")
                    try:
                        buyer = get_user_as_buyer(requesting_user)
                        existing_record = NegotiationRequest.objects.get(
                            Q(listing_id=ret.get("inventory_item_id")),
                            Q(buyer=buyer)
                        )
                        print("existing record")
                        if existing_record.listing_id:
                            ret.update(soldby="already_contacted")
                    except:
                        # We should keep going if the record doesn't exist.
                        ret.update(soldby="real_seller")
            else:
                ret.update(soldby="user_not_loggedin")

            userProfile = UserProfileSerializer(UserProfile.objects.get(user_id=seller_user_id)).data

            address = get_inventory_item_address(item_id=ret.get("inventory_item_id"))

            if address == None:
                address = userProfile
            else:
                address = InventoryItemAddressSerializer(address).data
                address["phone_primary"] = userProfile.get("phone_primary")
                address["phone_verified"] = userProfile.get("phone_verified", "false")
                address["email_verified"] = userProfile.get("email_verified", "false")

            ret.update(address=address)
            sanitized = sanitize_inventory_item(ret)

            return sanitized
        except Exception:
            traceback.print_exc()
            return sanitized

    def update(self, instance, validated_data):
        instance.inventory_item_id = validated_data.get('inventory_item_id', instance.inventory_item_id)
        instance.inventory_item_status = validated_data.get('inventory_item_status', instance.inventory_item_status)
        instance.product = validated_data.get('product', instance.product)
        instance.inventory_product_quantity = validated_data.get('inventory_product_quantity', instance.inventory_product_quantity)

        instance.product_measuring_unit = validated_data.get('product_measuring_unit', instance.product_measuring_unit)

        instance.inventory_item_id = validated_data.get('inventory_item_id', instance.inventory_item_id)
        instance.item_picture = validated_data.get('item_picture', instance.item_picture)
        instance.product_category = validated_data.get('product_category', instance.product_category)


# each inventory item can have its own address. Default is sellers address.
class InventoryItemAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItemAddress
        fields = '__all__'


# transporters have an id, their transportation capacity, and what they're willing to transport.
class TransporterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transporter
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class RegistrationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationStatus
        fields = '__all__'


class MyListingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

        depth = 6

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        sellerInstance = ret.get("seller")
        user_id = sellerInstance.get("seller").get("user_id")
        userProfile = UserProfileSerializer(UserProfile.objects.get(user_id=user_id)).data

        address = get_inventory_item_address(item_id=ret.get("inventory_item_id"))

        if address == None:
            address = userProfile
        else:
            address = InventoryItemAddressSerializer(address).data
            address["phone_primary"] = userProfile.get("phone_primary")
            address["phone_verified"] = userProfile.get("phone_verified", "false")
            address["email_verified"] = userProfile.get("email_verified", "false")

        ret.update(address=address)
        sanitized = sanitize_inventory_item(ret)

        return sanitized


class TextTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextTemplate
        fields = '__all__'


class NegotiationRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRequestStatus
        fields = '__all__'


class NegotiationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRequest
        fields = '__all__'


class MyNegotiationRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRequest
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        seller_name = get_seller_name(seller_id=ret.get("seller"))
        ret["seller_name"] = seller_name
        ret["listing_title"] = get_listing_title(listing_id=ret["listing_id"])

        return sanitize_negotiation_request_sent(ret)


class MyNegotiationRequestsSerializerReceived(serializers.ModelSerializer):
    class Meta:
        model = NegotiationRequest
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        buyer_id = ret.get("buyer")
        buyer = get_buyer_name(id=buyer_id)
        ret["buyer"] = buyer
        ret["listing_title"] = get_listing_title(listing_id=ret["listing_id"])

        return sanitize_negotiation_request_received(ret)

class PhoneOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = "__all__"