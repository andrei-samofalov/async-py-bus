from pybus.base.engine.events import EventEngine
from pybus.base.maps import EventHandlerMap
from pybus.base.routers.messagerouter import AbstractBaseMessageRouter


class EventRouter(AbstractBaseMessageRouter[EventEngine]):
    map_cls = EventHandlerMap
    engine_cls = EventEngine

    def get_engine(self):
        return self.engine_cls(message_map=self._map)
