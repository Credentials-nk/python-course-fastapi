from fastapi import FastAPI, HTTPException, Query, Body


app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {
        "id": 1,
        "title": "Hello from FastAPI",
        "content": "My fist post with FastAPI"
    },
    {
        "id": 2,
        "title": "Hey there",
        "content": "Good look everywhere"
    },
    {
        "id": 3,
        "title": "NL2SQL at City Hall",
        "content": "First step to let the mayor query data using natural language"
    }
]


@app.get("/")
def home():
    return {"message": "Welcome to my blog by Niko"}


@app.get("/posts")
def list_posts(
    query: str | None = Query(
        default=None,
        description="Test for search by title"
    )
):
    if query:
        results = [post for post in BLOG_POST if query.lower()
                   in post["title"].lower()]
        # for post in BLOG_POST:
        #     if query.lower() in post["title"].lower():
        #         results.append(post)
        return {"data": results, "query": query}

    return {"data": BLOG_POST}


@app.get("/posts/{post_id}")
def get_post(
    post_id: int,
    include_content: bool = Query(
        default=True,
        description="Flag to include content"
    )
):
    result = next((post for post in BLOG_POST if post["id"] == post_id), None)

    if result is None:
        return {"error": "Post not found"}

    if not include_content:
        result = {key: value for key, value in result.items() if key !=
                  "content"}

    return {"data": result, "include_content": include_content}


@app.post("/posts")
def create_post(post: dict = Body(...)):
    if "title" not in post or "content" not in post:
        return {"error": "Title and content is required"}

    if not str(post["title"].strip()):
        return {"error": "Title is empty"}

    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    new_post = {"id": new_id,
                "title": post["title"], "content": post["content"]}

    BLOG_POST.append(new_post)

    return {
        "message": "New post created successfully",
        "id": new_post
    }


@app.put("/posts/{post_id}")
def update_post(post_id: int, data: dict = Body(...)):
    for post in BLOG_POST:
        if post["id"] == post_id:
            if "title" in data:
                post["title"] = data["title"]
            if "content" in data:
                post["content"] = data["content"]
            return {"message": "Post updated", "data": post}

    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return

    raise HTTPException(status_code=404, detail="Post not found")
