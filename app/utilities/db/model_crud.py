from typing import Type

from pydantic import BaseModel
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import Base


async def create_model_instance(
    session: AsyncSession, model: Base, model_data: Type[BaseModel]
) -> Type[Base]:
    new_model = model(**model_data.model_dump())

    # Insert new company object into the db (without commiting)
    session.add(new_model)
    return new_model


async def update_model_instance(
    session: AsyncSession, model: Base, instance_id: int, model_data: Type[BaseModel]
) -> Type[Base]:
    query = (
        update(model)
        .where(model.id == instance_id)
        .values(
            {
                key: value
                for key, value in model_data.model_dump().items()
                if value is not None
            }
        )
        .returning(model)
    )
    res = await session.execute(query)
    await session.commit()
    return res.unique().scalar_one()


async def delete_model_instance(
    session: AsyncSession, model: Base, instance_id: int
) -> int:
    query = delete(model).where(model.id == instance_id).returning(model.id)

    result = (await session.execute(query)).scalar_one()
    await session.commit()
    return result