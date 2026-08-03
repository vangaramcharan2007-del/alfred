from __future__ import annotations
from typing import Dict, Any, List, Optional
from jarvisx.core.hermes import HermesBus
from jarvisx.core.events import Event
from jarvisx.capabilities.external.external_provider import Provider
from jarvisx.capabilities.coding.metrics import CodingMetrics

class ProviderRegistry:
    def __init__(
        self,
        bus: Optional[HermesBus] = None,
        metrics: Optional[CodingMetrics] = None
    ):
        self.bus = bus or HermesBus()
        self.metrics = metrics or CodingMetrics()
        self._providers: Dict[str, Provider] = {}

    async def register_provider(self, provider: Provider) -> None:
        try:
            connected = await provider.connect()
            if connected:
                self._providers[provider.name] = provider
                self.metrics.provider_connections += 1

                await self.bus.publish(Event(
                    type="provider.connected",
                    source="provider_registry",
                    payload={"provider": provider.name, "metadata": provider.metadata()}
                ))
            else:
                raise RuntimeError(f"Provider {provider.name} failed connection.")
        except Exception as e:
            self.metrics.failed_connections += 1
            await self.bus.publish(Event(
                type="provider.failed",
                source="provider_registry",
                payload={"provider": provider.name, "error": str(e)}
            ))
            raise e

    async def unregister_provider(self, name: str) -> bool:
        if name in self._providers:
            provider = self._providers[name]
            await provider.disconnect()
            del self._providers[name]

            await self.bus.publish(Event(
                type="provider.disconnected",
                source="provider_registry",
                payload={"provider": name}
            ))
            return True
        return False

    def get_provider(self, name: str) -> Optional[Provider]:
        return self._providers.get(name)

    def list_providers(self) -> List[Provider]:
        return list(self._providers.values())
