import django_tables2 as tables
from dcim.models import DeviceType
from django_tables2.utils import Accessor
from netbox.tables import NetBoxTable, columns

from .models import SoftwareImage

GOLDEN_IMAGE_PROGRESS_GRAPH = """
{% if record.golden_image %}
    {% if record.instances.count %}
        {% progress_graph record.golden_image.get_progress %}
    {% else %}
        No instances
    {% endif %}
{% else %}
    &mdash;
{% endif %}
"""

GOLDEN_IMAGE_ACTION = """
{% if record.golden_image %}
    <a href="{% url 'plugins:netbox_software_tracker:goldenimage_edit' pk=record.golden_image.pk %}" class="btn btn-sm btn-primary" title="Edit Image">
        <i class="mdi mdi-link" aria-hidden="true"></i>
    </a>
    <a href="{% url 'plugins:netbox_software_tracker:goldenimage_progress' pk=record.golden_image.pk %}" class="btn btn-sm btn-secondary" title="Out of Compliance">
        <i class="mdi mdi-history" aria-hidden="true"></i>
    </a>
    <a href="{% url 'plugins:netbox_software_tracker:goldenimage_delete' pk=record.golden_image.pk %}" class="btn btn-sm btn-danger" title="Clear image">
        <i class="mdi mdi-trash-can-outline" aria-hidden="true"></i>
    </a>
{% else %}
    <a href="{% url 'plugins:netbox_software_tracker:goldenimage_add' device_type_pk=record.pk %}" class="btn btn-sm btn-primary" title="Assign Image">
        <i class="mdi mdi-link" aria-hidden="true"></i>
    </a>
    <button class="btn btn-sm btn-secondary" title="Out of Compliance" disabled="disabled">
        <i class="mdi mdi-history" aria-hidden="true"></i>
    </button>
    <button class="btn btn-sm btn-danger" title="Clear image" disabled="disabled">
        <i class="mdi mdi-trash-can-outline" aria-hidden="true"></i>
    </button>
{% endif %}
"""


class SoftwareImageListTable(NetBoxTable):
    actions = columns.ActionsColumn()

    md5sum = tables.Column(
        verbose_name="MD5"
    )

    filename = tables.Column(
        verbose_name="File Name"
    )
    tags = columns.TagColumn(
        url_name="plugins:netbox_software_tracker:softwareimage_list"
    )

    class Meta(NetBoxTable.Meta):
        model = SoftwareImage
        fields = (
            "pk",
            "id",
            "filename",
            "version",
            "md5sum",
            "tags",
            "actions",
            "created",
            "last_updated",
        )
        default_columns = (
            "filename",
            "version",
            "size",
            "md5sum",
            "tags",
            "actions",
        )


class GoldenImageListTable(NetBoxTable):
    model = tables.LinkColumn(
        viewname="dcim:devicetype",
        args=[Accessor("pk")],
        verbose_name="Device Type",
    )

    version = tables.Column(
        linkify=("plugins:netbox_software_tracker:softwareimage", {"pk": tables.A("golden_image.software.id")}),
        accessor="golden_image.software.version",
    )

    md5sum = tables.Column(
        accessor="golden_image.software.md5sum",
        verbose_name="MD5"
    )

    filename = tables.Column(
        accessor="golden_image.software.filename",
        verbose_name="File Name"
    )

    comments = tables.Column(
        accessor="golden_image.software.comments",
    )

    progress = tables.TemplateColumn(
        template_code=GOLDEN_IMAGE_PROGRESS_GRAPH,
        orderable=False,
        verbose_name="Progress",
    )

    actions = tables.TemplateColumn(
        template_code=GOLDEN_IMAGE_ACTION,
        verbose_name="",
    )

    class Meta(NetBoxTable.Meta):
        model = DeviceType
        fields = (
            "model",
            "version",
            "md5sum",
            "filename",
            "progress",
            "comments"
        )

        default_columns = (
            "model",
            "version",
            "md5sum",
            "filename",
            "progress",
            "actions"
        )