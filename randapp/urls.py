from django.urls import path
from .views import upload_image  # Import only the upload_image view

urlpatterns = [
    path('', upload_image, name='upload'),  # Root URL serves the upload page
]
