from rest_framework import generics

from projects.models import Project
from projects.serializers import ProjectSerializer


class ProjectAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    # permission_classes = [permissions.IsAuthenticated, OwnBookPermission]
