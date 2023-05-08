import socket
import time
import sys
import enum
import types
import logging
import asyncio
import random
from typing import Awaitable

from ocacomms.OcaDiscovery import OcaDiscovery
from ocacore.ocp1 import *


class State(enum.Enum):
    DISCONNECTED = 0  # No session
    DISCOVERING = 1  # Browsing for services
    CONNECTING = 2  # Setting up a connection
    CONNECTED = 3  # Idle


T_KEEPALIVE_S: int = 5  # seconds
T_DISCOVERY_S: int = 0.5
RECV_IP: str = ""
RECV_PORT: int = 42042


class OCAClientProtocol:
    def __init__(self, receive_queue):
        self.transport = None
        self.receive_queue = receive_queue

    def connection_made(self, transport):
        self.transport = transport

    def send(self, message):
        self.message = message.bytes
        self.transport.sendto(self.message)
        # logging.debug(f"To device   --> {len(self.message)} bytes")

    def datagram_received(self, data, addr):
        # logging.debug(f"From device <-- {len(self.message)} bytes")
        self.receive_queue.put_nowait(data)
        # self.transport.close()

    def error_received(self, exc):
        logging.warn(f"From device <-- Error: {exc}")

    def connection_lost(self, exc):
        pass


class OCAController:
    def __init__(
        self: object,
        device_name: str,
        device_protocol: str,  # "udp" | "tcp" | "websocket"
    ) -> None:
        self.transport = None
        self.device_name: str = device_name
        self.device_protocol: str = device_protocol

        # Set up logging
        logging.basicConfig(
            format="[%(asctime)s][%(levelname)s]: \t%(message)s", level=logging.DEBUG
        )

        self._state_callbacks: dict = {
            State.DISCONNECTED: self._main_disconnected,
            State.DISCOVERING: self._main_discovering,
            State.CONNECTING: self._main_connecting,
            State.CONNECTED: self._main_connected,
        }
        self.state: int = State.DISCONNECTED
        self._cur_state_main: Awaitable = self._state_callbacks[self.state]

        self.transmit_task = None
        self.transmit_queue = asyncio.Queue()
        self.receive_task = None
        self.receive_queue = asyncio.Queue()
        
        self.unanswered_keepalives = 0
        self.session_active = asyncio.Event()


    # == == == == == Queue Consumers

    async def _transmit(self) -> None:
        """
        Send packets out when one is ready
        """
        loop = asyncio.get_event_loop()
        self.transport, self.protocol, = await loop.create_datagram_endpoint(
            lambda: OCAClientProtocol(self.receive_queue),
            remote_addr=(
                (
                    socket.inet_ntoa(self.device_service.addresses[0]),
                    self.device_service.port,
                )
            ),
        )
        while True:
            pkt = await self.transmit_queue.get()
            logging.info(f"Transmit: {type(pkt).__qualname__}")
            self.protocol.send(pkt)


    async def _receive(self) -> None:
        """
        Handle incoming data
        """
        while True:
            message = await self.receive_queue.get()
            try:
                pdu = marshal(message)
            except Exception as exc:
                logging.warning(f"Could not parse incoming data: {exc}")
            logging.info(f"Receive: {type(pdu).__qualname__}")
            
            if isinstance(pdu, Ocp1KeepAlivePdu):
                if not self.session_active.is_set():
                    self.session_active.set()
                self.unanswered_keepalives -= 1 if self.unanswered_keepalives > 0 else self.unanswered_keepalives


    # == == == == == Device Supervision
    
    async def _keepalive(self) -> None:
        """
        Maintain KeepAlive with the device
        AES70-3 5.3
        """
        keepalive_pkt = Ocp1KeepAlivePdu(
            header=Ocp1Header(
                protocol_version=1,
                message_size=11,
                message_type=MessageType.KEEPALIVE.value,
                message_count=1,
            ),
            heartbeat=T_KEEPALIVE_S,
        )
        while True:
            if self.unanswered_keepalives >= 3:
                self._state_transition(State.DISCONNECTED)
            self.transmit_queue.put_nowait(keepalive_pkt)
            self.unanswered_keepalives += 1
            await asyncio.sleep(T_KEEPALIVE_S)
    
    
    # == == == == == State management

    def _state_transition(self: object, new_state: int) -> None:
        """
        Handle any cleanup required from exiting current state, and any setup required for entering new state
        """
        logging.debug(f"Transition: {self.state} -> {new_state}")

        # Assume no action needed and safe to move
        self.state = new_state


    async def _main_disconnected(self: object) -> None:
        """
        Main tick for State.DISCONNECTED
        """
        raise NotImplementedError("#TODO handle reconnection")


    async def _main_discovering(self: object) -> None:
        """
        Main tick for State.DISCOVERING
        """
        self.discovery = OcaDiscovery(self.device_protocol)
        loop_counter = 0
        while True:
            if loop_counter > 30:
                raise TimeoutError(
                    "Could not discover {device}, available services: {services}".format(
                        device=self.device_name,
                        services=[service.name for service in self.discovery.services],
                    )
                )
            if service := self.discovery.find(self.device_name):
                self.device_service = service
                break
            await asyncio.sleep(T_DISCOVERY_S)
            loop_counter += 1

        logging.debug(
            f"Discovered {self.device_name}: {socket.inet_ntoa(self.device_service.addresses[0])}:{self.device_service.port}"
        )
        self._state_transition(State.CONNECTING)


    async def _main_connecting(self: object) -> None:
        """
        Main tick for State.CONNECTING
        """
        if self.device_protocol != "udp":
            raise NotImplementedError("Just working on UDP for now!")

        logging.debug("Start receive task")
        self.receive_task = asyncio.create_task(self._receive())
        logging.debug("Start transmit task")
        self.transmit_task = asyncio.create_task(self._transmit())
        logging.debug("Start keepalive task")
        self.keepalive_task = asyncio.create_task(self._keepalive())

        # Set by first keepalive response
        await self.session_active.wait()

        self._state_transition(State.CONNECTED)


    async def _main_connected(self: object) -> None:
        """
        Main tick for State.CONNECTED
        """
        await asyncio.sleep(0.1)

        # Demo
        for param in [0, 1]:
            pkt = Ocp1CommandPdu(
                header=Ocp1Header(
                    protocol_version=1,
                    message_size=28,
                    message_type=MessageType.COMMAND_RESPONSE_REQUIRED.value,
                    message_count=1,
                ),
                commands=[
                    Ocp1Command(
                        handle=1,
                        target_ono=0x3060058,
                        method_id=OcaMethodID(def_level=4, method_index=2),
                        parameters=Ocp1Parameters(parameters=[param]),
                    )
                ],
            )
            await self.transmit_queue.put(pkt)
            await asyncio.sleep(5)


    async def start(self: object) -> None:
        """
        Start loop
        """
        # Discover services & resolve address
        self._state_transition(State.DISCOVERING)
        while True:
            await self._state_callbacks[self.state]()


# == == == == ==


if __name__ == "__main__":
    controller = OCAController(sys.argv[1], sys.argv[2])
    asyncio.get_event_loop().run_until_complete(controller.start())
