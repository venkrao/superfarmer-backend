from .models import *
from superfarmer.settings import MEDIA_ROOT, MEDIA_URL
from collections import OrderedDict
import traceback

def get_user_registration_status(request):
    registration_status = None
    try:
        user = Users.objects.get(user_id=Users.objects.get(email_address=request.user.email).user_id)
        registration_status = RegistrationStatus.objects.get("status")
    except:
        pass

    return registration_status


def user_profile_exists(request):
    userprofile = None
    try:
        userprofile = UserProfile.objects.get(user_id=Users.objects.get(email_address=request.user.email))
    except:
        pass

    return userprofile


def get_user(request):
    try:
        user = Users.objects.get(email_address=request.user.email)
        print("user = {}".format(user))
        return user
    except:
        return None


def get_user_id_by_name(username=None):
    try:
        user = Users.objects.get(name=username)
        print("user = {}".format(user))
        return user.user_id
    except:
        return None


def get_product(product_name=None):
    try:
        product = Product.objects.get(product_name=product_name)
        return product
    except:
        return None


def is_seller(request):
    try:
        user_id = get_user(request)
        print("user_id = {}".format(user_id))
        seller = Seller.objects.get(seller=user_id)
        return seller
    except:
        print("{} is not a registered seller.".format(user_id))
        return None


def get_listing_details(listing_id=None):
    try:
        print("Looking for listing details of: {}".format(listing_id))
        listing_details = Inventory.objects.get(inventory_item_id=listing_id)
        print(listing_details)
        return listing_details
    except:
        print("No such listing: {}".format(listing_id))
        return None


def get_buyer_name(id=None, buyer_id=None):
    if id:
        buyer_id = Buyer.objects.get(id=id).buyer_id.user_id
        buyer_name = Users.objects.get(user_id=buyer_id).name
        return buyer_name

    if buyer_id:
        buyer_name = Users.objects.get(buyer_id=buyer_id).name
        return buyer_name

def get_user_as_buyer(user_id=None):
    try:
         buyer = Buyer.objects.get(buyer_id=user_id)
         return buyer
    except:
        print("get_user_as_buyer: No results for: {}".format(user_id))
        return None


def get_request_as_buyer(request=None):
    try:
        user_id = get_user(request).user_id
        buyer = get_user_as_buyer(user_id=user_id)
        return buyer
    except:
        print("get_request_as_buyer: No results for: {}".format(request))
        return None


def get_seller_of_listing(listing_id=None):
    listing_details = get_listing_details(listing_id=listing_id)
    try:
        return listing_details.seller
    except:
        print("get_seller_of_listing: No results for: {}".format(listing_id))
        return None


def get_seller(request=None):
    try:
        user_id = get_user(request)
        print("user_id = {}".format(user_id))
        seller = Seller.objects.get(seller=user_id)
        return seller
    except:
        print("{} is not a registered seller.".format(request.user_id))

        return None


def get_seller_from_id(user_id=None):
    try:
        seller = Seller.objects.get(seller=user_id)
        return seller
    except:
        print("{} is not a registered seller.".format(request.user_id))

        return None


def get_product_measuring_unit(measuring_unit=None):
    try:
        product_measuring_unit = MeasuringUnit.objects.get(measuring_unit=measuring_unit)
        return product_measuring_unit
    except:
        return None


def get_product_category(category=None, product=None):
    product_category = None
    if category:
        try:
            if type(category) == int:
                product_category = ProductCategory.objects.get(category_id=category)
            else:
                print("looking up category_id for: {}".format(category))
                product_category = ProductCategory.objects.get(category_name=category)
        except:
            print("No such category:  {}".format(category))

    if product:
        try:
            print("looking up product_category for product: {}".format(product))
            if type(product) == int:
                product_object = Product.objects.get(product_id=product.product_id)
            else:
                product_object = Product.objects.get(product_name=product.product_name)

            print("product object: ".format(product_object))
            product_category = ProductCategory.objects.get(category_id=product_object.product_category)
        except:
            print("Not found:  {}".format(product_category))

    print("product_cactegory: {}".format(product_category))
    return product_category


def handle_uploaded_file(f):
    filepath = "{}/{}".format(MEDIA_ROOT, f.name.replace("/","_"))
    try:
        with open(filepath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return "{}{}".format(MEDIA_URL, f)
    except:
        return "error"


def get_inventory_item_address(item_id=None):
    address = None
    try:
        address = InventoryItemAddress.objects.get(item_id=item_id)
    except:
        print("{} has no separate address assigned. Defaulting to seller's address.".format(item_id))

    return address


def get_seller_name(seller_id=None):
    seller_obj = Seller.objects.get(id=seller_id)
    seller_user_id = seller_obj.seller.user_id
    print("seller_user_id = {}".format(seller_user_id))
    user = Users.objects.get(user_id=seller_user_id)
    return user.name


def get_listing_title(listing_id=None):
    return get_listing_details(listing_id).listing_title


def sanitize_negotiation_request_sent(negotiationRequest=None):
    sanitized = OrderedDict()
    sanitized["listing_id"] = negotiationRequest.get("listing_id")
    sanitized["seller"] = negotiationRequest.get("seller_name")
    sanitized["request_body"] = negotiationRequest.get("request_body")
    sanitized["listing_title"] = negotiationRequest.get("listing_title")
    sanitized["sent_on"] = negotiationRequest.get("sent_on")
    sanitized["accepted"] = "Pending" if negotiationRequest.get("accepted") == False else "Rejected"

    return sanitized


def sanitize_negotiation_request_received(negotiationRequest=None):
    sanitized = OrderedDict()
    sanitized["listing_id"] = negotiationRequest.get("listing_id")
    sanitized["buyer"] = negotiationRequest.get("buyer")
    sanitized["request_body"] = negotiationRequest.get("request_body")
    sanitized["listing_title"] = negotiationRequest.get("listing_title")
    sanitized["sent_on"] = negotiationRequest.get("sent_on")
    sanitized["accepted"] = "Pending" if negotiationRequest.get("accepted") == False else "Rejected"

    return sanitized


def sanitize_user_address(userProfile=None):
    sanitized = OrderedDict()
    sanitized["about_seller"] = userProfile.get("about_me")
    sanitized["address"] = userProfile.get("address")
    sanitized["city"] = userProfile.get("city")
    sanitized["state"] = userProfile.get("state")
    sanitized["country"] = userProfile.get("country")
    sanitized["postal_code"] = userProfile.get("postal_code")
    sanitized["latitude"] = userProfile.get("latitude")
    sanitized["longitude"] = userProfile.get("longitude")
    sanitized["latitude"] = userProfile.get("latitude")

    sanitized["phone_primary"] = "Unavailable"

    if userProfile.get("phone_verified") == True:
        sanitized["phone_primary"] = userProfile.get("phone_primary")

    sanitized["email_verified"] = "Unavailable"
    if userProfile.get("email_verified") == True:
        sanitized["email_verified"] = userProfile.get("email_verified")

    return sanitized


def sanitize_inventory_item(instance):
    sanitized = OrderedDict()
    sanitized["inventory_item_id"] = instance.get("inventory_item_id")
    sanitized["listing_title"] = instance.get("listing_title")
    sanitized["item_price"] = instance.get("item_price")
    sanitized["inventory_product_quantity"] = instance.get("inventory_product_quantity")
    sanitized["inventory_item_create_datetime"] = instance.get("inventory_item_create_datetime")
    sanitized["inventory_item_update_datetime"] = instance.get("inventory_item_update_datetime")
    sanitized["inventory_available_from_datetime"] = instance.get("inventory_available_from_datetime")
    sanitized["item_picture"] = instance.get("item_picture")
    sanitized["inventory_item_status"] = instance.get("inventory_item_status").get("status")
    sanitized["product_name"] = instance.get("product").get("product_name")
    sanitized["product_category"] = instance.get("product").get("product_category").get("category_name")

    sanitized["seller_name"] = instance.get("seller").get("seller").get("name")
    sanitized["measuring_unit"] = instance.get("product_measuring_unit").get("measuring_unit")

    sanitized["soldby"] = instance.get("soldby", False)

    address = OrderedDict()

    address.update(address=instance.get("address").get("address"))
    address.update(city=instance.get("address").get("city"))
    address.update(state=instance.get("address").get("state"))
    address.update(country=instance.get("address").get("country"))
    address.update(latitude=instance.get("address").get("latitude"))
    address.update(longitude=instance.get("address").get("longitude"))
    address.update(phone_primary=instance.get("address").get("phone_primary"))
    address.update(phone_verified=instance.get("address").get("phone_verified"))
    address.update(email_verified=instance.get("address").get("email_verified"))

    sanitized["address"] = address



    return sanitized


def get_listings():
    listings = Inventory.objects.get()
    return listings


def get_listings_by_category(category=None):
    listings_by_category = None
    try:
        print("Looking up listings for category: {}".format(category))
        queryset = Inventory.objects.filter(product_category=category).values()
        print(queryset)
        listings_by_category = []
        for l in queryset:
            listings_by_category.append(l)
    except:
        print("No listings for category: {}".format(category))
        pass

    return listings_by_category


def get_inventory_item_instance(listing_id=None):
    try:
        instance = Inventory.objects.get(inventory_item_id=listing_id)
        return instance
    except:
        print("get_inventory_item_instance: No results for: {}".format(listing_id))
        return None