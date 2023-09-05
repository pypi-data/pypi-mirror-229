

from .sxm import StarXMediaRolesTemplate
from tendril.authz.roles.interests_approvals import InterestApprovalContextRolesMixin


class PlatformRoleSpec(StarXMediaRolesTemplate,
                       InterestApprovalContextRolesMixin):
    prefix = "platform"
    allowed_children = ['*']
    parent_required = False
    approval_role = 'Platform Media Approver'

    roles = ['Administrator',
             'Advertising Manager',
             'Media Manager',
             'Device Manager',
             'Member',
             'Platform Media Approver']
