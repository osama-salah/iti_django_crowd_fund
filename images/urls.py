
#
from django.urls import path

from images.images.views import display_image

urlpatterns = [
    # path('<image_name>/', display_image, name='display_image'),
    path('media/projects/images/<image_name>', display_image),
]
