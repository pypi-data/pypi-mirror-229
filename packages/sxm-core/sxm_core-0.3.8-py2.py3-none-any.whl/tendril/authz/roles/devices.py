

from .sxm import StarXMediaRolesTemplate
from tendril.authz.roles.interests_approvals import InterestApprovalRolesMixin
from tendril.authz.roles.interests_approvals import InterestApprovalContextRolesMixin


class FleetAgencyRoleSpec(StarXMediaRolesTemplate):
    prefix = 'fleet_agency'
    allowed_children = ['fleet_agency', 'fleet']
    roles = ['Administrator', 'Media Manager', 'Device Manager', 'Member']


class FleetRoleSpec(StarXMediaRolesTemplate,
                    InterestApprovalContextRolesMixin):
    prefix = 'fleet'
    allowed_children = ['fleet', 'device', 'device_content']
    roles = ['Administrator', 'Media Manager', 'Device Manager', 'Member', 'Fleet Media Approver']
    child_add_roles = {'device': 'Device Manager',
                       'device_content': 'Media Manager'}
    approval_role = 'Fleet Media Approver'


class DeviceRoleSpec(StarXMediaRolesTemplate):
    prefix = 'device'
    allowed_children = ['device_content']
    roles = ['Administrator', 'Media Manager', 'Device Manager', 'Member']
    edit_role = 'Device Manager'
    child_add_roles = {'device_content': 'Media Manager'}

    def _custom_actions(self):
        return {
            'read_settings': ('Member', f'{self.prefix}:read'),
            'write_settings': ('Device Manager', f'{self.prefix}:write')
        }


class DeviceContentRoleSpec(StarXMediaRolesTemplate,
                            InterestApprovalRolesMixin):
    prefix = 'device_content'
    allowed_children = []
    roles = ['Administrator', 'Media Manager', 'Member']
    edit_role = 'Media Manager'
    artefact_add_role = 'Media Manager'
    artefact_delete_role = 'Media Manager'
