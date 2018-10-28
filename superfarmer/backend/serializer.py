from .models import *
from rest_framework import serializers

class UserCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCategory
        fields = '__all__'


class UserStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStatus
        fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class UserContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserContactInfo
        fields = '__all__'


# List of categories the web portal is supporting.
class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


# a product has an id, and it belongs to a category.
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# each product has a measuring unit, a base measuring unit and a multiplier.
# measuring unit = multiplier * base measuring unit
class ProductMeasuringUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductMeasuringUnit
        fields = '__all__'

# list of sellers, with the list of products they sell.
class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'


# list of buyers, with the list of products they buy.
class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = '__all__'


# inventory item has a status: draft, active, suspended, unavailable.
class InventoryItemStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItemStatus
        fields = '__all__'


# a list of all advertised products.
class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


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


