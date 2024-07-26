from extras.scripts import *
from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site, Platform, Interface
from dcim.choices import InterfaceTypeChoices
from ipam.models import IPAddress

REGEX_IP_WITH_CIDR = ("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)"
                      "{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/[1-9][0-9]{0,1}$")

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

    device_manufacturer = ObjectVar(
        description="Select the device manufacturer",
        model=Manufacturer,
        required=True
    )

    device_type = ObjectVar(
        description="Select the device type",
        model=DeviceType,
        required=True,
        query_params={
            'manufacturer_id': '$device_manufacturer'
        }
    )

    device_platform = ObjectVar(
        description="Select the device platform",
        model=Platform,
        required=True,
        query_params={
            'manufacturer_id': '$device_manufacturer'
        }
    )

    device_role = ObjectVar(
        description="Select device role",
        model=DeviceRole,
        required=True
    )

    interface_name = StringVar(
        description="Define primary interface name",
        required=True
    )

    interface_description = StringVar(
        description="Define interface description",
        required=False
    )

    interface_type = ChoiceVar(
        InterfaceTypeChoices,
        default=InterfaceTypeChoices,
        description="Select interface type",
        required=True
    )

    interface_ip = StringVar(
        description="Enter interface IP address with CIDR notation. [regex validated]",
        required=True,
        regex=REGEX_IP_WITH_CIDR
    )

    device_primary_ip = BooleanVar(
        description="Is this interface IP also the device primary IP address?",
        required=True
    )

    def run(self, data, commit):

        # Create Device:

        new_device = Device(
            name=data['device_name'],
            site=data['site_name'],
            device_type=data['device_type'],
            platform=data['device_platform'],
            role=data['device_role'],
        )

        new_device.full_clean()
        new_device.save()
        self.log_success(f"Created new device: {new_device}")

        # Create Interface:

        new_interface = Interface(
            device=new_device,
            name=data['interface_name'],
            description=data['interface_description'],
            type=data['interface_type']
        )
        
        new_interface.full_clean()
        new_interface.save()
        self.log_success(f"Added new interface {new_interface} to device {new_device}")

        # Create IP Address:

        new_ip = IPAddress(
            address=data['interface_ip'],
            assigned_object=new_interface
        )

        new_interface.snapshot()
        # new_ip.full_clean() # Check for duplicates
        new_ip.save()
        self.log_success(f"Assigned new IP address {new_ip} to interface {new_interface}")

        if data['device_primary_ip'] is True:
            new_device.snapshot()
            new_device.primary_ip4=new_ip
            new_device.save()
            self.log_success(f"Device {new_device} has new primary ip: {new_ip}")