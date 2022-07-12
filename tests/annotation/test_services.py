import pytest

from annotation import models, services

pytestmark = pytest.mark.django_db


def test_import_dataset(group):
    services.import_dataset(
        dataset_rows_list=[{"foo": 1}, {"bar": 2}],
        dataset_label="foo",
        organization_id=group.id,
    )

    assert models.DatasetRow.objects.count() == 2
