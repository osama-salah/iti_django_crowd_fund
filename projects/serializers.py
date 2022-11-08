from rest_framework import serializers

from images.serializers import ImageSerializer
from projects.models import Project, Donation


class ProjectSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ("id", "title", "details", "category", "total_target", "tags",
                  "start_date", "end_date", "added_at", "images", "user_id", "rates")

    def create(self, validated_data):
        validated_data['user_id'] = self.context['request'].user
        tags = validated_data['tags']
        del validated_data['tags']
        created = Project.objects.create(**validated_data)
        created.tags.set(tags)
        return created


class DonationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Donation
        fields = ("user_id", "project_id", "amount", "date", )

    def create(self, validated_data):
        # validated_data['user_id'] = self.context['request'].user
        # project_id = validated_data['project_id']
        # del validated_data['project_id']
        created = Donation.objects.create(**validated_data)
        # created.project_id.set(project_id)
        return created
