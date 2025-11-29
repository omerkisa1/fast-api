from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import CreatePost, ResponsePost
from app.database import Post, create_db_and_tables, create_async_engine, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile

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

    temp_file_path = None

    try: 
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend_upload"]
            )
            )
        if upload_result.response_metadata.http_status_code == 200:

          
            post = Post(
                caption = caption,
                url = upload_result.url,
                file_type = "video" if file.content_type.startswith("video/") else "image",
                file_name = upload_result.name
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)
            return post
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

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