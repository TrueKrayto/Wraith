from sqlalchemy.orm import Session

from backend import models
from backend.entities.characters.resources import clamp_resource


def get_resource(
    db: Session,
    character_id: int,
    resource_name: str,
) -> models.CharacterResource:
    resource = (
        db.query(models.CharacterResource)
        .filter(
            models.CharacterResource.character_id == character_id,
            models.CharacterResource.name == resource_name,
        )
        .first()
    )

    if resource is None:
        raise ValueError(
            f"Character {character_id} has no resource named '{resource_name}'."
        )

    return resource


def change_resource(
    db: Session,
    character_id: int,
    resource_name: str,
    amount: int,
) -> models.CharacterResource:
    """
    Change a resource by a relative amount.

    Positive amounts restore/add.
    Negative amounts remove.
    Values are clamped between 0 and maximum.
    """
    resource = get_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
    )

    resource.current = clamp_resource(
        resource.current + amount,
        resource.maximum,
    )

    db.flush()

    return resource


def spend_resource(
    db: Session,
    character_id: int,
    resource_name: str,
    amount: int,
) -> models.CharacterResource:
    """
    Spend a resource only if enough is available.
    """
    if amount < 0:
        raise ValueError("Spend amount cannot be negative.")

    resource = get_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
    )

    if resource.current < amount:
        raise ValueError(
            f"Not enough {resource_name}. "
            f"Required: {amount}, available: {resource.current}."
        )

    return change_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
        amount=-amount,
    )

def restore_resource(
    db: Session,
    character_id: int,
    resource_name: str,
    amount: int,
) -> models.CharacterResource:
    """
    Restore a resource without exceeding its maximum.
    """
    if amount < 0:
        raise ValueError("Restore amount cannot be negative.")

    return change_resource(
        db=db,
        character_id=character_id,
        resource_name=resource_name,
        amount=amount,
    )