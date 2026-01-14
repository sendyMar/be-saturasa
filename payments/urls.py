from django.urls import path
from .views import CreateDummyPaymentView

urlpatterns = [
    path('create_dummy/', CreateDummyPaymentView.as_view(), name='create-dummy-payment'),
]
