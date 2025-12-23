from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
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
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None

    try:
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)

        # Upload to ImageKit (v5 syntax)
        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.upload_file(
                file=f,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend", "fastapi"]
            )

        # Validate upload
        if not upload_result or not upload_result.url:
            raise HTTPException(
                status_code=500, detail="Imagekit upload failed")

        # Save post in DB
        post = Post(
            caption=caption,
            url=upload_result.url,
            file_type="video" if file.content_type.startswith(
                "video/") else "image",
            file_name=upload_result.name
        )

        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()


@app.get("/feed")
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append({
            "id": str(post.id),
            "caption": post.caption,
            "url": post.url,
            "file_type": post.file_type,
            "file_name": post.file_name,
            "created_at": post.created_at.isoformat()
        })

    return {"posts": posts_data}

    # text_posts = {
    #     1: {"title": "First Steps", "content": "Kicking off the project with momentum"},
    #     2: {"title": "Learning FastAPI", "content": "Building APIs feels smooth and fast"},
    #     3: {"title": "Solo Dev Life", "content": "Iterating daily and loving the process"},
    #     4: {"title": "Python Tricks", "content": "List comprehensions make everything cleaner"},
    #     5: {"title": "Deep Work", "content": "Two focused hours beat a distracted day"},
    #     6: {"title": "Math Moment", "content": "Revisiting linear algebra to sharpen intuition"},
    #     7: {"title": "Writing Habit", "content": "Publishing daily builds clarity and momentum"},
    #     8: {"title": "ML Experiments", "content": "Trying out new models and documenting results"},
    #     9: {"title": "Workflow Upgrade", "content": "Automating repetitive tasks saves mental energy"},
    #     10: {"title": "Small Wins", "content": "Shipped a feature today — progress feels good"},
    # }

    # @app.get("/posts")
    # def get_all_posts(limit: int | None = None):
    #     posts = list(text_posts.values())
    #     if limit:
    #         return posts[:limit]
    #     return text_posts

    # @app.get("/posts/{id}")
    # def get_post(id: int):
    #     if id not in text_posts:
    #         raise HTTPException(status_code=404, detail="Post not found")
    #     return text_posts.get(id)

    # @app.post("/posts")
    # def create_post(post: PostCreate) -> PostResponse:
    # new_post = {"title": post.title, "content": post.content}
    # text_posts[max(text_posts.keys()) + 1] = new_post
    # return new_post
