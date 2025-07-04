from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel import select, Session

from typing import Annotated, List

from sqlmodel.ext.asyncio.session import AsyncSession

from migration.db import get_session

from migration.models.songs import Song, SongCreate

router = APIRouter()

@router.get("/songs", response_model=List[Song])
async def get_all_songs(session: Annotated[AsyncSession ,Depends(get_session)]):
    # sesssion.execute is deprecated
    result = (await session.exec(select(Song))).fetchall()

    # print("The Result Is: ", result)
    # print("The Length Of Result is: ", len(result) < 1)

    if len(result) < 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    
    # print("The Size Of is: ", result._allrows())

    # songs =  result.scalars().all() # The Old Way

    return [ Song(id=song.id, name=song.name, artist=song.artist) for song in result ]

@router.post("/song", response_model=Song)
async def create_new_song(song: SongCreate, session: Annotated[AsyncSession, Depends(get_session)]):
    data = Song(name=song.name, artist=song.artist)

    session.add(data)
    await session.commit()

    await session.refresh(data)

    return data