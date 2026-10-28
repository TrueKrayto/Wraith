from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from .clients.client import (
    get_llm_client,
    get_llm_model,
)


class LLMRole(StrEnum):
    """
    Explicit LLM responsibilities within Wraith.

    Systems request an LLM by role rather than by provider or model.
    """

    DEFAULT = "default"

    NPC_CREATION = "npc_creation"
    NPC_ENRICHMENT = "npc_enrichment"
    NPC_MUTATION = "npc_mutation"

    LOCATION_SHAPE = "location_shape"
    LOCATION_CREATION = "location_creation"
    LOCATION_ENRICHMENT = "location_enrichment"
    
    INTENT_EXTRACTION = "intent_extraction"

@dataclass(frozen=True)
class LLMClientSelection:
    """
    The client/model pair selected for a specific LLM role.
    """

    client: Any
    model: str


class LLMClientManager:
    """
    Central routing point for all Wraith LLM usage.

    Currently every role uses the same provider client and default model.

    Systems using this manager should not care which provider or model
    actually services a role. Provider/model routing can therefore change
    later without changing the calling systems.
    """

    def __init__(self):
        self._default_model = get_llm_model()

        self._client = get_llm_client()

        self._models: dict[LLMRole, str] = {
            role: self._default_model
            for role in LLMRole
        }

    def get(
        self,
        role: LLMRole | str,
    ) -> LLMClientSelection:
        """
        Return the client/model pair assigned to a role.
        """

        resolved_role = self._resolve_role(
            role
        )

        return LLMClientSelection(
            client=self._client,
            model=self._models[resolved_role],
        )

    def get_model(
        self,
        role: LLMRole | str,
    ) -> str:
        """
        Return only the model currently assigned to a role.
        """

        resolved_role = self._resolve_role(
            role
        )

        return self._models[
            resolved_role
        ]

    def set_model(
        self,
        role: LLMRole | str,
        model: str,
    ) -> None:
        """
        Change the model assigned to a role for the current runtime.
        """

        resolved_role = self._resolve_role(
            role
        )

        model = model.strip()

        if not model:
            raise ValueError(
                "LLM model cannot be empty."
            )

        self._models[
            resolved_role
        ] = model

    def reset_model(
        self,
        role: LLMRole | str,
    ) -> None:
        """
        Restore a role to the application's default model.
        """

        resolved_role = self._resolve_role(
            role
        )

        self._models[
            resolved_role
        ] = self._default_model

    def reset_all(
        self,
    ) -> None:
        """
        Restore every role to the application's default model.
        """

        for role in LLMRole:
            self._models[
                role
            ] = self._default_model

    @staticmethod
    def _resolve_role(
        role: LLMRole | str,
    ) -> LLMRole:
        """
        Convert a string role into the canonical enum.

        Unknown roles fail explicitly rather than silently falling
        back to another model.
        """

        if isinstance(
            role,
            LLMRole,
        ):
            return role

        try:
            return LLMRole(
                role
            )

        except ValueError as error:
            raise ValueError(
                f"Unknown LLM role: {role}"
            ) from error


# ==================================================================
# SHARED MANAGER
# ==================================================================

_llm_client_manager: LLMClientManager | None = None


def get_llm_client_manager(
) -> LLMClientManager:
    """
    Return the shared runtime LLM client manager.
    """

    global _llm_client_manager

    if _llm_client_manager is None:
        _llm_client_manager = (
            LLMClientManager()
        )

    return _llm_client_manager