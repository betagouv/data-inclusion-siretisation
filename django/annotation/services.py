from typing import Optional

from django.contrib.postgres import search
from django.db import models, transaction

from annotation.models import Dataset, DatasetRow
from sirene.models import Establishment


def import_dataset(
    dataset_rows_list: list[dict],
    dataset_label: str,
    organization_id: str,
):
    with transaction.atomic():
        dataset_instance = Dataset.objects.create(
            label=dataset_label,
            organization_id=organization_id,
        )

        for dataset_row_dict in dataset_rows_list:
            DatasetRow.objects.create(
                dataset=dataset_instance,
                data=dataset_row_dict,
            )


def search_sirene(
    *,
    adresse: Optional[str] = None,
    name: Optional[str] = None,
    postal_code: Optional[str] = None,
    siret: Optional[str] = None,
) -> models.QuerySet:

    # prevent searches based on the name only, because trigram similarity can not be
    # used on the whole sirene database
    if not any([postal_code, siret]):
        return Establishment.objects.none()

    establishment_qs = Establishment.objects

    if postal_code is not None:
        establishment_qs = establishment_qs.filter(postal_code__startswith=postal_code)

    if siret is not None:
        establishment_qs = establishment_qs.filter(siret__contains=siret)

    if name:
        establishment_qs = establishment_qs.annotate(
            name_similarity=search.TrigramWordSimilarity(name, "name")
        ).order_by("-name_similarity")

        if adresse is not None:
            establishment_qs = establishment_qs.filter(address1__iregex=adresse)

    elif adresse is not None:
        establishment_qs = establishment_qs.annotate(
            adresse_similarity=search.TrigramWordSimilarity(adresse, "address1")
        ).order_by("-adresse_similarity")

    return establishment_qs.all()
