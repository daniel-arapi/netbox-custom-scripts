from extras.scripts import *
from django.utils.text import slugify

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Platform
from dcim.models.device_components import Interface
from dcim.choices import DeviceStatusChoices, SiteStatusChoices
from virtualization.choices import VirtualMachineStatusChoices, ClusterStatusChoices
from virtualization.models import VirtualMachine, Cluster


class AddNewDevice(Script):
    class Meta:
        name = "Add New Device"
        description = "Add new device to a site"

    device_name = StringVar(
        description="Name of the new device"
    )

    # User to select one of the available site instances
    site_name = ObjectVar(
        description="The site which the new device will be added to",
        model=Site,
        required=True
    )

    manufacturer = ObjectVar(
        description="Select device vendor",
        model=Manufacturer,
        required=True
    )

    device_model = ObjectVar(
        description="Device model",
        model=DeviceType,
        query_params={
            'manufacturer': '$manufacturer'
        }
    )

    platform = ObjectVar(
        description="Select device software platform",
        model=Platform,
        required=True
    )

    primary_interface = StringVar(
        description="Primary interface name",
        required=False
    )

    primary_ip = StringVar(
        description="IP address of primary interface",
        required=False
    )

    def run(self, data, commit):
        device_name = data['device_name']
        site_name = data['site_name']
        manufacturer_name = data['manufacturer']
        platform_name = data['platform']

        manufacturer_name = Manufacturer.objects.get(name=manufacturer_name)

        new_device = Device(
            name=device_name,
            device_type=data['device_model'],
            # slug=slugify(device_name),
            site=site_name,
            # manufacturer=manufacturer_name,
            platform=platform_name,
            role=DeviceRole.objects.get(name='switch')

        )

        new_device.save()
        self.log_success(f"Created new switch: {new_device}")