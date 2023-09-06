
from dataclasses import asdict
from multiprocessing.connection import Connection
from time import sleep
from typing import Dict, List

from tb_vendor import models
from tb_vendor.mqtt.processes import ProcessConnTypedDict
from tb_vendor.telemetry.telemetry import VendorPolling

# str -> device_id
DeviceIdConnectionSearchDict = Dict[str, Connection]


#
# TODO: complete this function to be able to poll data from any vendor
# use abstract classes and methods
#

def polling_blocking(
    vendor: VendorPolling,
    tb_virtual_devices: List[models.TbVirtualDevice],
    multiproc_conn_list: List[ProcessConnTypedDict],
    polling_interval: float
):
    """Periodically polling data from vendor to generate Telemetry."""
    multiproc_conn_seach_dict: DeviceIdConnectionSearchDict = {}
    for multiproc_conn in multiproc_conn_list:
        multiproc_conn_seach_dict.update(
            {multiproc_conn["device_id"]: multiproc_conn["conn_dict"]["parent_conn"]}
        )

    while True:
        tb_virtual_devices = vendor.poll()
        for tb_virtual_device in tb_virtual_devices:
            try:
                parent_conn = multiproc_conn_seach_dict[tb_virtual_device.device_id]
            except KeyError:
                print(f"Key error {tb_virtual_device.device_id}")
                continue
            telemetry = tb_virtual_device.vendor_device.telemetry
            if telemetry:
                parent_conn.send(asdict(telemetry))

            # pprint(asdict(tb_virtual_device))
        sleep(polling_interval)
