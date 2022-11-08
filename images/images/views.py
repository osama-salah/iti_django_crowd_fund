from django.shortcuts import render
from rest_framework import viewsets

from images.serializers import ImageSerializer


# class ImageViewSet(viewsets.ModelViewSet):
#     # queryset = Book.objects.all()
#     serializer_class = ImageSerializer


def display_image(request, image_name):
    return render(request, 'images/view_image.html', context={'image_name': image_name})
