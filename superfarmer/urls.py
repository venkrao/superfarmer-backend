"""superfarmer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from django.conf.urls import url, include
from rest_framework import routers
from superfarmer.backend.views import *

router = routers.DefaultRouter()
router.register(r'usercategory', UserCategoryView)
router.register(r'userstatus', UserStatusView)
router.register(r'users', UsersView)

router.register(r'product', ProductView)
router.register(r'seller', SellerView)
router.register(r'buyer', BuyerView)
router.register(r'productcategory', ProductCategoryView)
router.register(r'productmeasuringunit', ProductMeasuringUnitView)
router.register(r'inventoryitemstatus', InventoryItemStatusView)
router.register(r'intentory', InventoryView)
router.register(r'inventoryitemaddress', InventoryItemAddressView)
router.register(r'registrationstatus', RegistrationStatusView)

router.register(r'transporter', TransporterView)


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'userauth', UserAuth.as_view()),
    url(r'userprofile', UserProfileView.as_view()),
    url(r'playgroundview', PlaygroundView.as_view())
]
