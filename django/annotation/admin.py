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
    list_display = ["id", "row", "siret", "created_at", "is_parent", "closed", "skipped"]
    list_filter = ["is_parent", "closed", "skipped"]
    search_fields = ["siret", "row__data__nom"]
