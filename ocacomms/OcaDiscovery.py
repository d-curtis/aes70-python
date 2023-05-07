"""
Discover registered OCA devices 
"""

from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
from typing import Union
import logging

class OcaListener:
    """
    Callback definitions to handle mDNS events
    """
    def __init__(self: object) -> None:
        self.services: list[ServiceInfo] = []

    def remove_service(self: object, zeroconf: Zeroconf, type: str, name: str) -> None:
        info = zeroconf.get_service_info(type, name)
        if info in self.services:
            self.services[self.services.index(info)].remove()
        logging.debug(
            f"{'[Browser] Removed':<20}" + 
            f"{info.type:<20}{info.parsed_addresses()[0]:<16}{info.port:<7}{name.strip(info.type)}"
        )

    def add_service(self: object, zeroconf: Zeroconf, type, name: str) -> None:
        info = zeroconf.get_service_info(type, name)
        if info not in self.services:
            self.services.append(info)
        logging.debug(
            f"{'[Browser] Added':<20}" + 
            f"{info.type:<20}{info.parsed_addresses()[0]:<16}{info.port:<7}{name.strip(info.type)}"
        )

    def update_service(self: object, zeroconf: Zeroconf, type, name: str) -> None:
        info = zeroconf.get_service_info(type, name)
        if info in self.services:
            self.services[self.services.index(info)] = info
        logging.debug(
            f"{'[Browser] Updated':<20}" + 
            f"{info.type:<20}{info.parsed_addresses()[0]:<16}{info.port:<7}{name.strip(info.type)}"
        )

    
class OcaDiscovery:
    def __init__(self: object, protocol: str) -> None:
        self.protocol:  str = protocol.lower()
        assert self.protocol in ["udp", "tcp"]
        self.listener = OcaListener()

        self.zeroconf:  Zeroconf = Zeroconf()
        self.browser:   ServiceBrowser = ServiceBrowser(self.zeroconf, f"_oca._{self.protocol}.local.", self.listener)
    
    @property
    def services(self) -> list[ServiceInfo]:
        return self.listener.services
    
    def find(self, device_name) -> Union[ServiceInfo, None]:
        for service in self.services:
            if service.name.split("._oca._udp.local.")[0].lower() == device_name.lower():
                return service


