from django.db import models
from django.utils.timezone import now


# admin, buyer, seller, buyer_treehugger, seller_treehugger.
class UserCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=32, unique=True)


# active, unverified, suspended, tobedeleted
class UserStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=32, unique=True)

# registered/pending
class RegistrationStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=32, unique=True)


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_status = models.ForeignKey(UserStatus, on_delete=models.CASCADE)
    email_address = models.EmailField(max_length=254, unique=True)
    name = models.CharField(max_length=128)
    member_since = models.DateTimeField(default=now)

    registration_status = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)


class UserProfile(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    about_me = models.CharField(max_length=512)
    address = models.CharField(max_length=126)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64, default="India")
    postal_code = models.CharField(max_length=18)
    latitude = models.FloatField(max_length=32, default="12.9716")
    longitude = models.FloatField(max_length=32, default="77.5946")
    phone_primary = models.CharField(max_length=32, unique=True)

    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)


# List of categories the web portal is supporting.
class ProductCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=64, unique=True)


# a product has an id, and it belongs to a category.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=64, unique=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_default_image = models.CharField(max_length=124)


# each product has a measuring unit, a base measuring unit and a multiplier.
# measuring unit = multiplier * base measuring unit
class ProductMeasuringUnit(models.Model):
    measuring_unit_id = models.AutoField(primary_key=True)
    base_measuring_unit = models.CharField(max_length=32)
    measuring_unit = models.CharField(max_length=32, unique=True)
    multiplier = models.FloatField()


# list of sellers, with the list of products they sell.
class Seller(models.Model):
    seller = models.ForeignKey(Users, on_delete=models.CASCADE)
    sells = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("seller", "sells")


# list of buyers, with the list of products they buy.
class Buyer(models.Model):
    buyer_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    buys = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("buyer_id", "buys")


# inventory item has a status: draft, active, suspended, unavailable.
class InventoryItemStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=16, unique=True)


# a list of all advertised products.
# TODO: item_picture must accept a picture, upload it to web server.
class Inventory(models.Model):
    inventory_item_id = models.BigAutoField(primary_key=True)
    inventory_item_status = models.ForeignKey(InventoryItemStatus, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    inventory_product_quantity = models.FloatField()
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    product_measuring_unit = models.ForeignKey(ProductMeasuringUnit, on_delete=models.PROTECT)
    inventory_item_create_datetime = models.DateTimeField(default=now)
    inventory_item_update_datetime = models.DateTimeField(default=now)
    inventory_available_from_datetime = models.DateTimeField(default=now)
    item_picture = models.CharField(max_length=124)


# each inventory item can have its own address. Default is sellers address.
class InventoryItemAddress(models.Model):
    item_id = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    address_part1 = models.CharField(max_length=126)
    address_part2 = models.CharField(max_length=126)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64, default="India")
    postal_code = models.CharField(max_length=18)
    latitude = models.FloatField(max_length=18)
    longitude = models.FloatField(max_length=18)


# transporters have an id, their transportation capacity, and what they're willing to transport.
# TODO:
# transporting capacity must be a positive floating point value. Impose the restriction in the model definition

class Transporter(models.Model):
    transporter_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    minimum_capacity = models.DecimalField(max_digits=9, decimal_places=0)
    max_capacity = models.DecimalField(max_digits=9, decimal_places=0)
    transports = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("transporter_id", "transports")

