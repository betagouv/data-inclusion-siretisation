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
    }

    postal_code_str = row_instance.task_data["code_postal"]
    name_str = row_instance.task_data["nom"]

    # prevent searches based on the name only, because trigram similarity can not be
    # used on the whole sirene database
    if not any([postal_code_str]):
        context["establishment_queryset"] = Establishment.objects.none()
        return render(request, "annotation/task.html", context)

    establishment_qs = Establishment.objects

    if postal_code_str:
        establishment_qs = establishment_qs.filter(postal_code__startswith=postal_code_str)

    if name_str:
        establishment_qs = establishment_qs.annotate(
            similarity=TrigramSimilarity("full_search_text", name_str)
        ).order_by("-similarity")

    establishment_qs = establishment_qs.all()[:10]

    context["establishment_queryset"] = establishment_qs

    return render(request, "annotation/task.html", context)


def search(request):
    unsafe_siret = request.POST.get("siret", "")
    unsafe_postal_code = request.POST.get("code_postal", "")
    unsafe_name = request.POST.get("nom", "")

    # prevent searches based on the name only, because trigram similarity can not be
    # used on the whole sirene database
    if not any([unsafe_siret, unsafe_postal_code]):
        context = {"establishment_queryset": Establishment.objects.none()}
        return render(request, "annotation/search.html", context)

    establishment_qs = Establishment.objects

    if unsafe_postal_code != "":
        establishment_qs = establishment_qs.filter(postal_code__startswith=unsafe_postal_code)

    if unsafe_siret != "":
        establishment_qs = establishment_qs.filter(siret__contains=unsafe_siret)

    if unsafe_name != "":
        establishment_qs = establishment_qs.annotate(
            similarity=TrigramSimilarity("full_search_text", unsafe_name)
        ).order_by("-similarity")

    establishment_qs = establishment_qs.all()[:10]

    context = {"establishment_queryset": establishment_qs}

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
