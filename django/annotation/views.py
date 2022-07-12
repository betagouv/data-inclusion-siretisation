from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Count
from django.shortcuts import render

from annotation.models import Annotation, DatasetRow
from sirene.models import Establishment


def progress(request):
    progress_current = DatasetRow.objects.annotate(Count("annotations")).filter(annotations__count__gt=0).count()
    progress_total = DatasetRow.objects.count()

    context = {
        "dataset_str": "cd35_annuaire_social",
        "progress_str": f"{progress_current} / {progress_total}",
        "completed": DatasetRow.objects.annotate(Count("annotations")).filter(annotations__count__gt=0).count()
        == DatasetRow.objects.count(),
        "annotations_queryset": Annotation.objects.all(),
    }

    return render(request, "annotation/progress.html", context)


def task(request):
    row_instance = DatasetRow.objects.annotate(Count("annotations")).exclude(annotations__count__gt=0).first()
    progress_current = DatasetRow.objects.annotate(Count("annotations")).filter(annotations__count__gt=0).count()
    progress_total = DatasetRow.objects.count()

    if row_instance is None:
        return progress(request)

    context = {
        "dataset_str": "cd35_annuaire_social",
        "progress_str": f"{progress_current} / {progress_total}",
        "row_instance": row_instance,
        "establishment_queryset": Establishment.objects.filter(
            postal_code__startswith=row_instance.data["code_postal"],
        )
        .annotate(similarity=TrigramSimilarity("full_search_text", row_instance.data["nom"]))
        .order_by("-similarity")[:10],
    }
    return render(request, "annotation/task.html", context)


def search(request):
    context = {
        "establishment_queryset": Establishment.objects.filter(
            siret__contains=request.POST["siret"],
            postal_code__startswith=request.POST["code_postal"],
        )
        .annotate(similarity=TrigramSimilarity("full_search_text", request.POST["nom"]))
        .order_by("-similarity")[:10],
    }

    return render(request, "annotation/search.html", context)


def submit(request):
    if request.POST.get("skipped", False):
        Annotation.objects.create(
            skipped=True,
            row_id=request.POST["row_instance_id"],
        )
    else:
        Annotation.objects.create(
            siret=request.POST["siret"],
            row_id=request.POST["row_instance_id"],
        )

    return task(request)


def index(request):
    return render(request, "annotation/index.html")
