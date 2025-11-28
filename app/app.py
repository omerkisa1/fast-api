from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, ResponsePost
from app.database import Post, create_db_and_tables, create_async_engine, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/upload")
async def upload_file(    
    file: UploadFile = File(...),
    caption: str = Form(""),
    db: AsyncSession = Depends(get_async_session)
    ):
    post = Post(
        caption = caption,
        url = "test url",
        file_type = "image",
        file_name = "test name"
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post

@app.get("/feed")
async def get_feed(
    db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.format()
            }
        )
    return {"posts": posts_data}