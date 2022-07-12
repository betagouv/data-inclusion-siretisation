from collections import defaultdict

from django.contrib.auth.models import Group
from django.db import models

from common.models import BaseModel


class Dataset(BaseModel):
    label = models.CharField(max_length=100)
    organization = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="datasets",
    )

    def __str__(self) -> str:
        return self.label


class DatasetRow(BaseModel):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.PROTECT,
        related_name="rows",
    )
    data = models.JSONField(default=dict)

    @property
    def task_data(self):
        data = defaultdict(None, self.data)

        return {
            "nom": data["nom"],
            "adresse": data["adresse"],
            "code_postal": data["code_postal"],
            "commune": data["commune"],
            "lien source": data["lien_source"],
            "typologie": data["typologie"],
            "description": data["presentation_resume"],
        }

    def __str__(self) -> str:
        return self.data["nom"]


class Annotation(BaseModel):
    row = models.ForeignKey(
        DatasetRow,
        on_delete=models.CASCADE,
        related_name="annotations",
    )
    siret = models.CharField(
        max_length=14,
        blank=True,
        default="",
    )
    skipped = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.siret} <-> {self.row.data['nom']}"
