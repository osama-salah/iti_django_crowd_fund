import os

from django.db import models

from projects.models import Project


class Image(models.Model):
    image = models.ImageField(null=True, upload_to='images/')
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.image)

    def delete(self, using=None, keep_parents=False):
        try:
            cwd = os.getcwd()
            url = str(self.image.url)[1:]
            image_url = os.path.join(cwd, url)
            os.remove(image_url)
        except FileNotFoundError:
            print('image not found: ', self.image.url)
        finally:
            super().delete()


class ProjectImage(Image):
    image = models.ImageField(null=True, upload_to='projects/images/')
