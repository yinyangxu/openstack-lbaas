import balancer.drivers.cisco_ace.ace_driver
import balancer.drivers.haproxy.HaproxyDriver

from balancer.db import api as db_api


DEVICE_DRIVERS = {}


# TODO(yorik-sar): add dynamic loading and config
def get_device_driver(conf, device_id):
    try:
        return DEVICE_DRIVERS[device_id]
    except KeyError:
        device_ref = db_api.device_get(conf, device_id)
        if device_ref['type'].lower() == "ace":
            cls = balancer.drivers.cisco_ace.ace_driver.AceDriver
        elif device_ref['type'].lower() == "haproxy":
            cls = balancer.drivers.haproxy.HaproxyDriver.HaproxyDriver
        else:
            raise NotImplementedError("Driver not found for type %s" % \
                                        (device_ref['type'],))
        return cls(conf, device_ref)