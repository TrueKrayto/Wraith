from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend import schemas

from backend.level_2_services.game import execute_action

from backend.level_4_systems.data import (
    Character,
    CharacterAttribute,
    CharacterResource,
    CharacterSkill,
    get_db,
)

from backend.level_4_systems.llm.clients import (
    get_llm_client,
    get_llm_model,
)

from backend.level_4_systems.llm.game import (
    ActionProposal,
    interpret_player_action,
    narrate_action,
)

from backend.level_4_systems.llm.npc import (
    decide_npc_action,
)


router = APIRouter(
    prefix="/play",
    tags=["play"],
)


def build_scene_context(
    db: Session,
    actor_character_id: int,
) -> str:
    """
    TEMPORARY:

    Build legacy SQLAlchemy character context for the LLM.

    This orchestration will later move into a Level 2 narrative
    service.
    """

    characters = db.query(Character).all()

    lines = []

    for character in characters:
        label = (
            "ACTOR"
            if character.id == actor_character_id
            else "PRESENT"
        )

        lines.append(
            f"{label}: character_id={character.id}, "
            f"name={character.name}, "
            f"role={character.role}, "
            f"level={character.level}"
        )

        attributes = (
            db.query(CharacterAttribute)
            .filter(
                CharacterAttribute.character_id
                == character.id
            )
            .all()
        )

        skills = (
            db.query(CharacterSkill)
            .filter(
                CharacterSkill.character_id
                == character.id
            )
            .all()
        )

        resources = (
            db.query(CharacterResource)
            .filter(
                CharacterResource.character_id
                == character.id
            )
            .all()
        )

        lines.append(
            "Attributes: "
            + ", ".join(
                f"{attribute.name}={attribute.value}"
                for attribute in attributes
            )
        )

        lines.append(
            "Skills: "
            + ", ".join(
                f"{skill.name}={skill.level}"
                for skill in skills
            )
        )

        lines.append(
            "Resources: "
            + ", ".join(
                f"{resource.name}="
                f"{resource.current}/{resource.maximum}"
                for resource in resources
            )
        )

        lines.append("")

    return "\n".join(lines)


def build_npc_context(
    db: Session,
    npc_character_id: int,
) -> dict:
    """
    TEMPORARY:

    Build the legacy NPC context supplied to the NPC decision LLM.
    """

    npc = (
        db.query(Character)
        .filter(
            Character.id == npc_character_id
        )
        .first()
    )

    if npc is None:
        raise ValueError(
            f"NPC character {npc_character_id} does not exist."
        )

    attributes = (
        db.query(CharacterAttribute)
        .filter(
            CharacterAttribute.character_id
            == npc.id
        )
        .all()
    )

    skills = (
        db.query(CharacterSkill)
        .filter(
            CharacterSkill.character_id
            == npc.id
        )
        .all()
    )

    resources = (
        db.query(CharacterResource)
        .filter(
            CharacterResource.character_id
            == npc.id
        )
        .all()
    )

    return {
        "character_id": npc.id,
        "name": npc.name,
        "role": npc.role,
        "level": npc.level,

        "attributes": {
            attribute.name: attribute.value
            for attribute in attributes
        },

        "skills": {
            skill.name: skill.level
            for skill in skills
        },

        "resources": {
            resource.name: {
                "current": resource.current,
                "maximum": resource.maximum,
            }
            for resource in resources
        },
    }


def get_responding_npc_id(
    proposal: ActionProposal,
) -> int | None:
    actor_id = proposal.actor_character_id

    if (
        proposal.target_character_id is not None
        and proposal.target_character_id != actor_id
    ):
        return proposal.target_character_id

    for check in proposal.checks:
        if (
            check.target_character_id is not None
            and check.target_character_id != actor_id
        ):
            return check.target_character_id

    return None


@router.post("")
def play_action(
    request: schemas.PlayerActionRequest,
    db: Session = Depends(get_db),
):
    try:
        # ---------------------------------
        # Select LLM
        # ---------------------------------

        client = get_llm_client()
        model = get_llm_model()

        # ---------------------------------
        # Player action
        # ---------------------------------

        player_scene_context = build_scene_context(
            db=db,
            actor_character_id=request.actor_character_id,
        )

        player_proposal = interpret_player_action(
            client=client,
            model=model,
            actor_character_id=request.actor_character_id,
            action_text=request.action_text,
            scene_context=player_scene_context,
        )

        player_result = execute_action(
            db=db,
            proposal=player_proposal,
        )

        # ---------------------------------
        # NPC response
        # ---------------------------------

        npc_proposal = None
        npc_result = None

        responding_npc_id = get_responding_npc_id(
            player_proposal
        )

        if responding_npc_id is not None:
            npc_context = build_npc_context(
                db=db,
                npc_character_id=responding_npc_id,
            )

            npc_scene_context = build_scene_context(
                db=db,
                actor_character_id=responding_npc_id,
            )

            npc_proposal = decide_npc_action(
                client=client,
                model=model,
                npc_character_id=responding_npc_id,
                npc_context=npc_context,
                scene_context=npc_scene_context,
                player_action=request.action_text,
                player_result=player_result,
                proposal_schema=ActionProposal,
            )

            npc_result = execute_action(
                db=db,
                proposal=npc_proposal,
            )

        # ---------------------------------
        # Persist resolved mechanics
        # ---------------------------------

        db.commit()

        # ---------------------------------
        # Narrate complete exchange
        # ---------------------------------

        narration = narrate_action(
            client=client,
            model=model,
            player_action=request.action_text,
            proposal=player_proposal,
            result=player_result,
            npc_proposal=npc_proposal,
            npc_result=npc_result,
        )

        return {
            "narration": narration,
            "proposal": player_proposal,
            "result": player_result,
            "npc_proposal": npc_proposal,
            "npc_result": npc_result,
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )