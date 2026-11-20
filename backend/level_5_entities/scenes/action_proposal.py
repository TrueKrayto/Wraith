
from typing import Literal

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


# ------------------------------------------------------------------
# INDIVIDUAL PROPOSED ACTION
# ------------------------------------------------------------------

class ProposedAction(BaseModel):
    """
    One action the player proposes to perform.

    Represents an attempt, never a resolved outcome.

    Actions may be conditional or dependent on the
    successful completion of earlier actions.

    Targets may be identified using canonical IDs.
    """

    # Broad category:
    # movement, combat, communication, observation, etc.
    action_type: str

    # What the player is attempting.
    intent: str

    # --------------------------------------------------------------
    # TARGET IDENTIFICATION
    # --------------------------------------------------------------

    # Original reference used to identify the target.
    #
    # Example:
    # "I attack the guard beside the doorway."
    #
    # target_reference = "guard beside the doorway"

    target_reference: str | None = None

    # Canonical ID of the intended target.
    #
    # NPC targets must use an existing npc_id.
    #
    # The proposer may only select IDs supplied
    # in its scene context.
    #
    # The backend must verify the ID before
    # passing the action to mechanical resolution.
    #
    # None means no canonical target was identified
    # or the action does not require one.

    target_id: str | None = None

    # Category of the identified target.
    #
    # Examples:
    # npc, location, object, item
    #
    # None when no canonical type is established.

    target_type: str | None = None

    # How the target was identified.
    #
    # explicit:
    # The player's reference identifies one entity.
    #
    # contextual:
    # Scene information or conversational context
    # identifies the intended entity.
    #
    # default:
    # Multiple plausible targets exist and a
    # reasonable default has been selected.
    #
    # unresolved:
    # No suitable canonical target was identified.
    #
    # None:
    # The action requires no target identification.

    target_resolution: Literal[
    "explicit",
    "contextual",
    "default",
    "descriptive",
    "unresolved",
    ] | None = None

    # --------------------------------------------------------------
    # DESTINATION
    # --------------------------------------------------------------

    # Intended destination, when applicable.
    destination_reference: str | None = None

    # --------------------------------------------------------------
    # COMMUNICATION AND ORIGINAL INPUT
    # --------------------------------------------------------------

    # Exact spoken words, if supplied.
    dialogue: str | None = None

    # Relevant fragment of the original player input.
    original_text: str | None = None

    # --------------------------------------------------------------
    # CONDITIONAL EXECUTION
    # --------------------------------------------------------------

    # An event or state that must occur before this
    # action should be attempted.
    #
    # Example:
    # "If Silversong attacks me, I dodge."
    #
    # condition = "Silversong attacks the player"
    #
    # None means no explicit condition was supplied.

    condition: str | None = None

    # --------------------------------------------------------------
    # ACTION DEPENDENCIES
    # --------------------------------------------------------------

    # Earlier actions whose successful outcomes are
    # required before this action can proceed.
    #
    # References use 1-based action positions.
    #
    # Example:
    # 1. Attempt to unlock door
    # 2. Open door if unlocking succeeds
    #
    # Action 2:
    # depends_on = [1]
    #
    # Ordinary action ordering does NOT imply dependency.

    depends_on: list[int] = Field(
        default_factory=list
    )


# ------------------------------------------------------------------
# COMPLETE ACTION PROPOSAL
# ------------------------------------------------------------------

class ActionProposal(BaseModel):
    """
    Structured proposal generated from player input.

    Actions preserve their original order.

    Canonical target IDs are proposals and require
    deterministic validation before use.

    This structure contains no:
    - success/failure outcomes
    - mechanical resolutions
    - resource mutations
    - world-state changes
    - NPC responses
    """

    actions: list[ProposedAction] = Field(
        default_factory=list
    )

    # References the proposer could not
    # confidently identify.
    #
    # These do not automatically invalidate the
    # player's entire action proposal.

    unresolved_references: list[str] = Field(
        default_factory=list
    )

    # --------------------------------------------------------------
    # VALIDATE ACTION DEPENDENCIES
    # --------------------------------------------------------------

    @model_validator(mode="after")
    def validate_dependencies(self):

        for index, action in enumerate(
            self.actions,
            start=1,
        ):

            if len(action.depends_on) != len(
                set(action.depends_on)
            ):
                raise ValueError(
                    f"Action {index} contains duplicate dependencies."
                )

            for dependency in action.depends_on:

                if dependency < 1:
                    raise ValueError(
                        "Action dependencies must use "
                        "1-based action positions."
                    )

                if dependency >= index:
                    raise ValueError(
                        f"Action {index} cannot depend on "
                        f"action {dependency}. Dependencies "
                        "must reference earlier actions."
                    )

        return self
