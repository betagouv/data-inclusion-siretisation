from django import http
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from annotation import services
from annotation.models import Annotation, Dataset, DatasetRow


@login_required()
def index(request: http.HttpRequest):
    unsafe_dataset_slug_str = request.GET.get("dataset", None)

    try:
        dataset_instance = Dataset.objects.get(slug=unsafe_dataset_slug_str)
    except Dataset.DoesNotExist:
        return http.HttpResponseNotFound()

    if not request.user.groups.filter(id=dataset_instance.organization.id).exists():
        return http.HttpResponseForbidden()

    context = {"dataset_instance": dataset_instance}

    return render(request, "annotation/index.html", context)


@login_required()
def partial_task(request: http.HttpRequest):
    if not request.htmx:
        return http.HttpResponseNotFound()

    unsafe_dataset_instance_id = request.GET.get("dataset_instance_id", None)

    try:
        dataset_instance = Dataset.objects.get(id=unsafe_dataset_instance_id)
    except Dataset.DoesNotExist:
        return http.HttpResponseNotFound()

    row_instance = (
        DatasetRow.objects.annotate(Count("annotations"))
        .filter(dataset_id=unsafe_dataset_instance_id)
        .exclude(annotations__count__gt=0)
        .first()
    )
    progress_current = (
        DatasetRow.objects.annotate(Count("annotations"))
        .filter(dataset_id=unsafe_dataset_instance_id)
        .filter(annotations__count__gt=0)
        .count()
    )
    progress_total = DatasetRow.objects.filter(dataset_id=unsafe_dataset_instance_id).count()

    if row_instance is None:
        return http.HttpResponse("Vous avez terminé ! :)")

    context = {
        "dataset_str": dataset_instance.label,
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
def partial_search(request: http.HttpRequest):
    if not request.htmx:
        return http.HttpResponseNotFound()

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
def partial_submit(request: http.HttpRequest):
    if not request.htmx:
        return http.HttpResponseNotFound()

    unsafe_dataset_instance_id = request.POST.get("dataset_instance_id", None)
    unsafe_row_instance_id = request.POST.get("row_instance_id", None)
    unsafe_skipped = request.POST.get("skipped", None)
    unsafe_closed = request.POST.get("closed", None)
    unsafe_irrelevant = request.POST.get("irrelevant", None)
    unsafe_is_parent = request.POST.get("is_parent", None)
    unsafe_siret = request.POST.get("siret", None)

    if not DatasetRow.objects.filter(dataset_id=unsafe_dataset_instance_id).filter(id=unsafe_row_instance_id).exists():
        return http.HttpResponseBadRequest()

    Annotation.objects.create(
        row_id=unsafe_row_instance_id,
        skipped=bool(unsafe_skipped),
        closed=bool(unsafe_closed),
        irrelevant=bool(unsafe_irrelevant),
        is_parent=bool(unsafe_is_parent),
        siret=unsafe_siret if unsafe_siret is not None else "",
        created_by=request.user,
    )

    context = {
        "skipped": unsafe_skipped,
        "irrelevant": unsafe_irrelevant,
        "is_parent": unsafe_is_parent,
        "closed": unsafe_closed,
    }

    return render(request, "annotation/submit.html", context)
