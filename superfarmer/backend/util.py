from .models import *
from superfarmer.settings import MEDIA_ROOT, MEDIA_URL

def get_user(request):
    try:
        user = Users.objects.get(email_address=request.user.email)
        return user
    except:
        return None


def get_product(product_name=None):
    try:
        product = Product.objects.get(product_name=product_name)
        return product
    except:
        return None


def get_seller(request):
    try:
        seller = Seller.objects.get(pk=get_user(request).user_id)
        return seller
    except:
        return None


def get_product_measuring_unit(measuring_unit=None):
    try:
        product_measuring_unit = ProductMeasuringUnit.objects.get(measuring_unit=measuring_unit)
        return product_measuring_unit
    except:
        return None


def handle_uploaded_file(f):
    filepath = "{}/{}".format(MEDIA_ROOT, f.name.replace("/","_"))
    try:
        with open(filepath, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        return "{}{}".format(MEDIA_URL, f)
    except:
        return "error"

