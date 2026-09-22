import json

from backend import models, schemas
from backend.database import SessionLocal
from backend.llm.interpreter import interpret_player_action
from backend.llm.narrator import narrate_action
from backend.llm.npc_agent import decide_npc_action
from backend.services.action_executor import execute_action


PLAYER_CHARACTER_ID = 1
NPC_CHARACTER_ID = 3


def main():
    db = SessionLocal()

    try:
        player = (
            db.query(models.Character)
            .filter(
                models.Character.id == PLAYER_CHARACTER_ID
            )
            .first()
        )

        npc = (
            db.query(models.Character)
            .filter(
                models.Character.id == NPC_CHARACTER_ID
            )
            .first()
        )

        if player is None:
            raise ValueError(
                f"Player character {PLAYER_CHARACTER_ID} does not exist."
            )

        if npc is None:
            raise ValueError(
                f"NPC character {NPC_CHARACTER_ID} does not exist."
            )

        player_action = (
            f"I punch {npc.name} in the face."
        )

        request = schemas.PlayerActionRequest(
            actor_character_id=player.id,
            action_text=player_action,
        )

        print()
        print("PLAYER ACTION")
        print("-------------")
        print(player_action)

        # ---------------------------------
        # Interpret player action
        # ---------------------------------

        player_proposal = interpret_player_action(
            db=db,
            request=request,
        )

        print()
        print("PLAYER ACTION PROPOSAL")
        print("----------------------")
        print(
            json.dumps(
                player_proposal.model_dump(),
                indent=2,
            )
        )

        # ---------------------------------
        # Execute player action
        # ---------------------------------

        player_result = execute_action(
            db=db,
            proposal=player_proposal,
        )

        print()
        print("PLAYER ACTION RESULT")
        print("--------------------")
        print(
            json.dumps(
                player_result,
                indent=2,
            )
        )

        # ---------------------------------
        # NPC decides response
        # ---------------------------------

        npc_proposal = decide_npc_action(
            db=db,
            npc_character_id=npc.id,
            player_action=player_action,
            player_result=player_result,
        )

        print()
        print("NPC ACTION PROPOSAL")
        print("-------------------")
        print(
            json.dumps(
                npc_proposal.model_dump(),
                indent=2,
            )
        )

        # ---------------------------------
        # Execute NPC response
        # ---------------------------------

        npc_result = execute_action(
            db=db,
            proposal=npc_proposal,
        )

        print()
        print("NPC ACTION RESULT")
        print("-----------------")
        print(
            json.dumps(
                npc_result,
                indent=2,
            )
        )

        # ---------------------------------
        # Narrate complete exchange
        # ---------------------------------

        narration = narrate_action(
            player_action=player_action,
            proposal=player_proposal,
            result=player_result,
            npc_proposal=npc_proposal,
            npc_result=npc_result,
        )

        print()
        print("NARRATED EXCHANGE")
        print("-----------------")
        print(narration)

        # ---------------------------------
        # Undo test changes
        # ---------------------------------

        db.rollback()

        print()
        print("Test transaction rolled back.")

    finally:
        db.close()


if __name__ == "__main__":
    main()