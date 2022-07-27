from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from annotation import services
from annotation.models import Annotation, DatasetRow


@login_required()
def index(request):
    return render(request, "annotation/index.html")


@login_required()
def partial_progress(request):
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


@login_required()
def partial_task(request):
    row_instance = DatasetRow.objects.annotate(Count("annotations")).exclude(annotations__count__gt=0).first()
    progress_current = DatasetRow.objects.annotate(Count("annotations")).filter(annotations__count__gt=0).count()
    progress_total = DatasetRow.objects.count()

    if row_instance is None:
        return partial_progress(request)

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


@login_required()
def partial_search(request):
    unsafe_address = request.POST.get("adresse", None)
    unsafe_name = request.POST.get("nom", None)
    unsafe_postal_code = request.POST.get("code_postal", None)
    unsafe_siret = request.POST.get("siret", None)

    context = {
        "establishment_queryset": services.search_sirene(
            adresse=unsafe_address,
            name=unsafe_name,
            postal_code=unsafe_postal_code,
            siret=unsafe_siret,
        )[:10]
    }

    return render(request, "annotation/search.html", context)


@login_required()
def partial_submit(request):
    unsafe_row_instance_id = request.POST.get("row_instance_id", None)
    unsafe_skipped = request.POST.get("skipped", None)
    unsafe_closed = request.POST.get("closed", None)
    unsafe_irrelevant = request.POST.get("irrelevant", None)
    unsafe_is_parent = request.POST.get("is_parent", None)
    unsafe_siret = request.POST.get("siret", None)

    Annotation.objects.create(
        row_id=unsafe_row_instance_id,
        skipped=bool(unsafe_skipped),
        closed=bool(unsafe_closed),
        irrelevant=bool(unsafe_irrelevant),
        is_parent=bool(unsafe_is_parent),
        siret=unsafe_siret if unsafe_siret is not None else "",
        created_by=request.user,
    )

    return partial_task(request)
