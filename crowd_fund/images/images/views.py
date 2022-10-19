from django.shortcuts import render
from rest_framework import viewsets


class ImageViewSet(viewsets.ModelViewSet):
    # queryset = Book.objects.all()
    serializer_class = ImageSerializer
