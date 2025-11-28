from fastapi import FastAPI, HTTPException
from app.schemas import CreatePost, ResponsePost
from app.database import Post, create_db_and_tables, create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/test")
def test():
    return{"message": "test"}


text_post_db = {
    1: {"title:": "Morning Vibes", "content:": "Starting the day with coffee and good energy."},
    2: {"title:": "Throwback", "content:": "Missing those summer nights already."},
    3: {"title:": "Daily Motivation", "content:": "Small steps every day lead to big changes."},
    4: {"title:": "Food Mood", "content:": "Just tried a new pasta recipe and wow."},
    5: {"title:": "Tech Moment", "content:": "Finally fixed that annoying bug today!"},
    6: {"title:": "Random Thought", "content:": "Why does time go faster on weekends?"},
    7: {"title:": "Music Share", "content:": "On repeat: my new favorite chill playlist."},
    8: {"title:": "Workout Log", "content:": "Leg day… send help."},
    9: {"title:": "Life Update", "content:": "Trying to balance work, life, and everything in between."},
    10: {"title:": "Night Mood", "content:": "Nothing beats quiet late-night walks."}
}


@app.get("/posts/{id}")
def get_posts(id: int):
    if id not in text_post_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_post_db.get(id)
    
@app.post("/posts")
def create_post(post: CreatePost) -> ResponsePost:
    new_post = {"title": post.title, "content": post.content}
    text_post_db[max(text_post_db.keys()) + 1] = new_post
    return new_post