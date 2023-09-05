

from tendril.libraries.interests.base import GenericInterestLibrary
from tendril.libraries.interests.manager import InterestLibraryManager

from tendril.interests.fleet_agency import FleetAgency
from tendril.interests.fleet import Fleet
from tendril.interests.device import Device
from tendril.interests.device_content import DeviceContent
from tendril.libraries.mixins.content import ContentLibraryMixin
from tendril.libraries.mixins.interests_approvals import ApprovalsLibraryMixin
from tendril.libraries.mixins.interests_approvals import ApprovalContextLibraryMixin
from tendril.libraries.mixins.interests_monitors import MonitorsLibraryMixin

from tendril.config import DEVICE_CONTENT_TYPES_ALLOWED


class FleetAgencyLibrary(GenericInterestLibrary,
                         MonitorsLibraryMixin):
    interest_class = FleetAgency


class FleetLibrary(GenericInterestLibrary,
                   MonitorsLibraryMixin,
                   ApprovalContextLibraryMixin):
    interest_class = Fleet


class DeviceLibrary(GenericInterestLibrary,
                    MonitorsLibraryMixin):
    enable_creation_api = False
    interest_class = Device


class DeviceContentLibrary(ContentLibraryMixin,
                           ApprovalsLibraryMixin,
                           GenericInterestLibrary):
    interest_class = DeviceContent
    media_types_allowed = DEVICE_CONTENT_TYPES_ALLOWED


def load(manager: InterestLibraryManager):
    manager.install_library('fleet_agencies', FleetAgencyLibrary())
    manager.install_library('fleets', FleetLibrary())
    manager.install_library('devices', DeviceLibrary())
    manager.install_library('device_content', DeviceContentLibrary())
