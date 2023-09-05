

from functools import lru_cache
from sqlalchemy import Column
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from tendril.db.models.deviceconfig import DeviceConfigurationModel
from tendril.db.models.deviceconfig import cfg_option_spec
from tendril.db.models.content import MediaContentInfoTModel
from tendril.common.states import LifecycleStatus
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class SXMDeviceConfigurationModel(DeviceConfigurationModel):
    device_type = "sxm"
    id = Column(Integer, ForeignKey(DeviceConfigurationModel.id), primary_key=True)

    allow_local_usb = Column(Boolean, nullable=False, default=False)
    portrait = Column(Boolean, nullable=False, default=False)
    flip = Column(Boolean, nullable=False, default=False)
    default_content_id = Column(Integer, ForeignKey('DeviceContent.id'))

    @declared_attr
    def default_content(cls):
        return relationship('DeviceContentModel', lazy='selectin')

    def _unpack_content(self, content_id):
        if not content_id:
            # TODO defer to fleet-level policy here
            return None
        if content_id != self.default_content_id:
            raise ValueError("Expecting content_id to be default_content_id")
        if not self.default_content.status == LifecycleStatus.ACTIVE:
            logger.warn(f"Configured default_content {self.default_content_id} "
                        f"for device {self.id} is not ACTIVE. Not sending.")
            content_id = None
        if not content_id:
            # TODO defer to fleet-level policy here
            return None
        dc = self.default_content.content
        return dc.export(full=False, explicit_durations_only=True)

    @classmethod
    @lru_cache(maxsize=None)
    def configuration_spec(cls):
        rv = super(SXMDeviceConfigurationModel, cls).configuration_spec()
        rv['display'] = {'portrait': cfg_option_spec('Portait Orientation', 'portrait',
                                                     type=bool, default=False),
                         'flip': cfg_option_spec('Flip Display Orientation', 'flip',
                                                 type=bool, default=False)}
        rv['local_usb'] = {'allow': cfg_option_spec('Allow local USB content', 'allow_local_usb',
                                                    type=bool, default=False)}
        rv['content'] = {'default': cfg_option_spec('Default Device Content', 'default_content_id',
                                                    validator='_device_content_validator',
                                                    exporter='_unpack_content', export_tmodel=MediaContentInfoTModel,
                                                    type=int, default=None)}
        return rv

    __mapper_args__ = {
        "polymorphic_identity": device_type,
    }
