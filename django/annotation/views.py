from django.db.models import Count
from django.shortcuts import render

from annotation import services
from annotation.models import Annotation, DatasetRow


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
        "establishment_queryset": services.search_sirene(
            adresse=row_instance.task_data["adresse"],
            name=row_instance.task_data["nom"],
            postal_code=row_instance.task_data["code_postal"],
            siret=row_instance.task_data["siret"],
        )[:10],
    }

    return render(request, "annotation/task.html", context)


def search(request):
    unsafe_address = request.POST.get("adresse", "")
    unsafe_name = request.POST.get("nom", "")
    unsafe_postal_code = request.POST.get("code_postal", "")
    unsafe_siret = request.POST.get("siret", "")

    context = {
        "establishment_queryset": services.search_sirene(
            adresse=unsafe_address,
            name=unsafe_name,
            postal_code=unsafe_postal_code,
            siret=unsafe_siret,
        )[:10]
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
