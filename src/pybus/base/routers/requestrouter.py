from pybus.base.engine.requests import RequestEngine
from pybus.base.maps import RequestHandlerMap
from pybus.base.routers.messagerouter import AbstractBaseMessageRouter


class RequestRouter(AbstractBaseMessageRouter[RequestEngine]):
    map_cls = RequestHandlerMap
    engine_cls = RequestEngine

    def get_engine(self):
        return self.engine_cls(event_engine=self._dispatcher.events.engine, message_map=self._map)
