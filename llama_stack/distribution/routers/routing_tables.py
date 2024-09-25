# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the terms described in the LICENSE file in
# the root directory of this source tree.

from typing import Any, List, Optional, Tuple

from llama_models.sku_list import resolve_model
from llama_models.llama3.api.datatypes import *  # noqa: F403

from llama_stack.apis.models import *  # noqa: F403
from llama_stack.apis.shields import *  # noqa: F403
from llama_stack.apis.memory_banks import *  # noqa: F403

from llama_stack.distribution.datatypes import *  # noqa: F403


class CommonRoutingTableImpl(RoutingTable):
    def __init__(
        self,
        inner_impls: List[Tuple[str, Any]],
        routing_table_config: Dict[str, List[RoutableProviderConfig]],
    ) -> None:
        self.providers = {k: v for k, v in inner_impls}
        self.routing_keys = list(self.providers.keys())
        self.routing_table_config = routing_table_config

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        for p in self.providers.values():
            await p.shutdown()

    def get_provider_impl(self, routing_key: str) -> Any:
        if routing_key not in self.providers:
            raise ValueError(f"Could not find provider for {routing_key}")
        return self.providers[routing_key]

    def get_routing_keys(self) -> List[str]:
        return self.routing_keys

    def get_provider_config(self, routing_key: str) -> Optional[GenericProviderConfig]:
        for entry in self.routing_table_config:
            if entry.routing_key == routing_key:
                return entry
        return None


class ModelsRoutingTable(CommonRoutingTableImpl, Models):

    async def list_models(self) -> List[ModelServingSpec]:
        specs = []
        for entry in self.routing_table_config:
            model_id = entry.routing_key
            specs.append(
                ModelServingSpec(
                    llama_model=resolve_model(model_id),
                    provider_config=entry,
                )
            )
        return specs

    async def get_model(self, core_model_id: str) -> Optional[ModelServingSpec]:
        for entry in self.routing_table_config:
            if entry.routing_key == core_model_id:
                return ModelServingSpec(
                    llama_model=resolve_model(core_model_id),
                    provider_config=entry,
                )
        return None


class ShieldsRoutingTable(CommonRoutingTableImpl, Shields):

    async def list_shields(self) -> List[ShieldSpec]:
        specs = []
        for entry in self.routing_table_config:
            specs.append(
                ShieldSpec(
                    shield_type=entry.routing_key,
                    provider_config=entry,
                )
            )
        return specs

    async def get_shield(self, shield_type: str) -> Optional[ShieldSpec]:
        for entry in self.routing_table_config:
            if entry.routing_key == shield_type:
                return ShieldSpec(
                    shield_type=entry.routing_key,
                    provider_config=entry,
                )
        return None


class MemoryBanksRoutingTable(CommonRoutingTableImpl, MemoryBanks):

    async def list_available_memory_banks(self) -> List[MemoryBankSpec]:
        specs = []
        for entry in self.routing_table_config:
            specs.append(
                MemoryBankSpec(
                    bank_type=entry.routing_key,
                    provider_config=entry,
                )
            )
        return specs

    async def get_serving_memory_bank(self, bank_type: str) -> Optional[MemoryBankSpec]:
        for entry in self.routing_table_config:
            if entry.routing_key == bank_type:
                return MemoryBankSpec(
                    bank_type=entry.routing_key,
                    provider_config=entry,
                )
        return None