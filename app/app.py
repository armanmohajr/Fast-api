from fastapi import FastAPI, HTTPException

app = FastAPI()

text_posts = {
    1: {"title": "First Steps", "content": "Kicking off the project with momentum"},
    2: {"title": "Learning FastAPI", "content": "Building APIs feels smooth and fast"},
    3: {"title": "Solo Dev Life", "content": "Iterating daily and loving the process"},
    4: {"title": "Python Tricks", "content": "List comprehensions make everything cleaner"},
    5: {"title": "Deep Work", "content": "Two focused hours beat a distracted day"},
    6: {"title": "Math Moment", "content": "Revisiting linear algebra to sharpen intuition"},
    7: {"title": "Writing Habit", "content": "Publishing daily builds clarity and momentum"},
    8: {"title": "ML Experiments", "content": "Trying out new models and documenting results"},
    9: {"title": "Workflow Upgrade", "content": "Automating repetitive tasks saves mental energy"},
    10: {"title": "Small Wins", "content": "Shipped a feature today — progress feels good"},
}


@app.get("/posts")
def get_all_posts(limit: int | None = None):
    posts = list(text_posts.values())
    if limit:
        return posts[:limit]
    return text_posts


@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts.get(id)
