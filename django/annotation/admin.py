from django.contrib import admin
from django.utils import text

from annotation import models


@admin.register(models.Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DatasetRow)
class DatasetRowAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "siret", "created_at", "is_parent", "closed", "skipped", "created_by"]
    list_filter = ["is_parent", "closed", "skipped", "created_by"]
    search_fields = ["siret", "row__data__nom"]

    def name(self, obj):
        return text.Truncator(obj.row.data["nom"]).chars(80)
