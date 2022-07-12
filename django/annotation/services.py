from django.db import transaction

from annotation import models


def import_dataset(
    dataset_rows_list: list[dict],
    dataset_label: str,
    organization_id: str,
):
    with transaction.atomic():
        dataset_instance = models.Dataset.objects.create(
            label=dataset_label,
            organization_id=organization_id,
        )

        for dataset_row_dict in dataset_rows_list:
            models.DatasetRow.objects.create(
                dataset=dataset_instance,
                data=dataset_row_dict,
            )
