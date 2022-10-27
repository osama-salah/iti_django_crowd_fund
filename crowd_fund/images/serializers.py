from rest_framework import serializers

from images.models import ProjectImage


class ImageSerializer(serializers.StringRelatedField):
    class Meta:
        model = ProjectImage
        fields = ("image", "project_id", )

    def get_fields(self):
        fields = super().get_fields()
        print(fields['image'])
        return fields
