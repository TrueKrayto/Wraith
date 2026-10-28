from pydantic import (
    BaseModel,
    Field,
    model_validator,
)


# ------------------------------------------------------------------
# INDIVIDUAL PLAYER ACTION
# ------------------------------------------------------------------

class IntentAction(BaseModel):
    """
    One action the player intends to perform.

    Represents an attempt, never a resolved outcome.

    Actions may be conditional or dependent on the
    successful completion of earlier actions.
    """

    # Broad category:
    # movement, combat, communication, observation, etc.
    action_type: str

    # What the player is attempting.
    intent: str

    # Entity, person, object, or subject being targeted.
    target_reference: str | None = None

    # Intended destination, when applicable.
    destination_reference: str | None = None

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
    # 2. Enter door, if unlocking succeeds
    #
    # Action 2:
    # depends_on = [1]
    #
    # Ordinary action ordering does NOT imply dependency.

    depends_on: list[int] = Field(
        default_factory=list
    )


# ------------------------------------------------------------------
# COMPLETE INTENT RESULT
# ------------------------------------------------------------------

class IntentResult(BaseModel):
    """
    Structured interpretation of player input.

    Actions preserve their original order.

    This structure contains no:
    - success/failure outcomes
    - mechanical resolutions
    - resource mutations
    - world-state changes
    - NPC responses
    """

    actions: list[IntentAction] = Field(
        default_factory=list
    )

    # References the extractor could not
    # confidently identify.
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