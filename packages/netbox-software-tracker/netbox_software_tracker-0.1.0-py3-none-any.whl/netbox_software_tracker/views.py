from dcim.models import DeviceType
from dcim.tables.devices import DeviceTable
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse
from netbox.views import generic

from .filtersets import GoldenImageFilterSet, SoftwareImageFilterSet
from .forms import (
    GoldenImageFilterForm,
    GoldenImageForm,
    SoftwareImageFilterForm,
    SoftwareImageForm,
)
from .models import GoldenImage, SoftwareImage
from .tables import GoldenImageListTable, SoftwareImageListTable


class GoldenImageView(generic.ObjectView):
    queryset = GoldenImage.objects.prefetch_related("tags")


class GoldenImageListView(generic.ObjectListView):
    template_name = "netbox_software_tracker/goldenimage_list.html"
    queryset = DeviceType.objects.prefetch_related("tags")
    table = GoldenImageListTable
    filterset = GoldenImageFilterSet
    filterset_form = GoldenImageFilterForm
    actions = ()


class GoldenImageProgressListView(generic.ObjectListView):
    queryset = GoldenImage.objects.all()
    actions = ()

    def get(self, request, pk: int, *args, **kwargs):
        instances = GoldenImage.objects.prefetch_related("device_type").filter(pk=pk)
        devices = []
        for item in instances:
            devices = devices + list(item.device_type.instances.all())

        return render(
            request,
            "netbox_software_tracker/goldenimage_progress.html",
            {
                "table": DeviceTable(devices),
            },
        )


class GoldenImageDeleteView(generic.ObjectDeleteView):
    queryset = GoldenImage.objects

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:goldenimage_list")


class GoldenImageEditView(generic.ObjectEditView):
    queryset = GoldenImage.objects
    form = GoldenImageForm

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:goldenimage_list")


class GoldenImageAssignView(generic.ObjectEditView):
    queryset = GoldenImage.objects
    form = GoldenImageForm

    def get(self, request, device_type_pk: int, *args, **kwargs):
        instance = GoldenImage(device_type=DeviceType.objects.get(pk=device_type_pk))
        form = GoldenImageForm(instance=instance)
        return render(
            request,
            "generic/object_edit.html",
            {
                "object": instance,
                "form": form,
                "return_url": reverse("plugins:netbox_software_tracker:goldenimage_list"),
            },
        )

    def post(self, request, *args, **kwargs):
        device_type = request.POST.get("device_type", None)
        software = request.POST.get("software", None)
        print("############", device_type)
        gi = GoldenImage.objects.create(
            device_type=DeviceType.objects.get(pk=device_type), software=SoftwareImage.objects.get(pk=software)
        )
        gi.save()

        messages.success(request, f"Assigned Golden Image for {device_type}: {gi.software}")
        return redirect(reverse("plugins:netbox_software_tracker:goldenimage_list"))


class SoftwareImageView(generic.ObjectView):
    queryset = SoftwareImage.objects.all()


class SoftwareImageList(generic.ObjectListView):
    queryset = SoftwareImage.objects.all()
    table = SoftwareImageListTable
    filterset = SoftwareImageFilterSet
    filterset_form = SoftwareImageFilterForm
    #actions = ("add", "delete", "bulk_delete", "bulk_edit")


class SoftwareImageAdd(generic.ObjectEditView):
    queryset = SoftwareImage.objects.all()
    form = SoftwareImageForm

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:softwareimage_list")


class SoftwareImageEdit(generic.ObjectEditView):
    queryset = SoftwareImage.objects.all()
    form = SoftwareImageForm


class SoftwareImageDelete(generic.ObjectDeleteView):
    queryset = SoftwareImage.objects.all()

    def get_return_url(self, *args, **kwargs) -> str:
        return reverse("plugins:netbox_software_tracker:softwareimage_list")


class SoftwareImageBulkDelete(generic.BulkDeleteView):
    queryset = SoftwareImage.objects.all()
    table = SoftwareImageListTable
