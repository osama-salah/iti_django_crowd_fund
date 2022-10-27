from django.contrib import admin

from images.models import ProjectImage
from projects.models import Project, ProjectCategory, ProjectTag

admin.site.register(ProjectCategory)
admin.site.register(ProjectTag)


class ImageAdmin(admin.StackedInline):
    model = ProjectImage


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ImageAdmin]

    class Meta:
        model = Project
