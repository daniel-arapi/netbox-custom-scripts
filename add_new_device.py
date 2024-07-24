from markdown_it.rules_inline.backticks import regex

from extras.scripts import *
from django.utils.text import slugify


from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Platform, Interface
from ipam.models import IPAddress
from dcim.choices import DeviceStatusChoices, SiteStatusChoices, InterfaceTypeChoices
from virtualization.choices import VirtualMachineStatusChoices, ClusterStatusChoices
from virtualization.models import VirtualMachine, Cluster


class AddNewDevice(Script):
    class Meta:
        name = "Add New Device"
        description = "Add new device to a site"

    name = StringVar(
        description="Name of the new device"
    )

    # User to select one of the available site instances
    site = ObjectVar(
        description="The site which the new device will be added to",
        model=Site,
        required=True
    )

    manufacturer = ObjectVar(
        description="Select the device manufacturer",
        model=Manufacturer,
        required=True
    )

    device_type = ObjectVar(
        description="Select the device type",
        model=DeviceType,
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )

    platform = ObjectVar(
        description="Select the device platform",
        model=Platform,
        required=True,
        query_params={
            'manufacturer_id': '$manufacturer'
        }
    )

    role = ObjectVar(
        description="Select device role",
        model=DeviceRole,
        required=True
    )

    add_primary_interface = BooleanVar(

    )

    primary_interface = StringVar(
        description="Primary interface name",
        required=True
    )

    interface_types = ChoiceVar(
        InterfaceTypeChoices,
        default=InterfaceTypeChoices,
        description="Interface Type Choices",
        required=True
    )

    primary_ip = StringVar(
        description="IP address of primary interface (regex validated)",
        required=False,
        regex="^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"
    )

    def run(self, data, commit):

        new_device = Device(
            name=data['name'],
            site=data['site'],
            device_type=data['device_type'],
            platform=data['platform'],
            role=data['role'],
        )

        new_device.full_clean()
        new_device.save()
        self.log_success(f"Created new device: {new_device}")

        if new_device:

            new_interface = Interface(
                device=new_device,
                name=data['primary_interface'],
                type=data['interface_types']
            )
            new_interface.full_clean()
            new_interface.save()
            self.log_success(f"Created interface: {new_interface}")

            # if new_interface:
            #     ipaddr = IPAddress(address=data['primary_ip'])
            #     ipaddr.full_clean()
            #     ipaddr.save()
            #
            #     print(ipaddr)
            #
            #
            #     new_interface.snapshot()
            #     new_interface.ip_addresses.set(ipaddr)