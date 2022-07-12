from django.contrib import admin

from annotation import models


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DatasetRow)
class DatasetRowAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    pass
