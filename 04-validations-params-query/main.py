from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(title="Mini Blog")

BLOG_POST = [
    {"id": 1, "title": "Hello from FastAPI", "content": "My fist post with FastAPI"},
    {"id": 2, "title": "Hey there", "content": "Good look everywhere"},
    {
        "id": 3,
        "title": "NL2SQL at City Hall",
        "content": "First step to let the mayor query data using natural language",
    },
]


class Tag(BaseModel):
    name: str = Field(..., min_length=3, max_length=30, description="Tag name")


class Author(BaseModel):
    name: str = Field(..., min_length=5, max_length=30, description="Author name")
    email: EmailStr = Field(..., description="Author email")


class PostBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []
    author: Optional[Author] = None


class PostCreate(PostBase):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Title of Post(min 3 character, max 100)",
        examples=["Mi first post in FastAPI"],
    )
    content: str = Field(
        default="Content not available",
        min_length=10,
        description="Content example for Post",
        examples=["This an available content Post"],
    )
    tags: List[Tag] = Field(default_factory=list)  # []

    @field_validator("title")
    @classmethod
    def not_allowed_title(cls, value: str) -> str:
        if "spam" in value.lower():
            raise ValueError("The title cannot contain the word: 'spam'")
        return value


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    content: Optional[str] = None


class PostPublic(PostBase):
    id: int


class PostSummary(BaseModel):
    id: int
    title: str


@app.get("/")
def home():
    return {"message": "Welcome to my blog by Niko"}


@app.get("/posts", response_model=List[PostPublic])
def list_posts(
    query: str | None = Query(default=None, description="Test for search by title"),
):
    if query:
        return [post for post in BLOG_POST if query.lower() in post["title"].lower()]

    return BLOG_POST


@app.get(
    "/posts/{post_id}",
    response_model=Union[PostPublic, PostSummary],
    response_description="Post found",
)
def get_post(
    post_id: int = Path(
        ...,
        ge=1,
        lt=4,
        title="ID Post",
        description="Identifier of Post. Should be gretter tan 1.",
        example=1,
    ),
    include_content: bool = Query(default=True, description="Flag to include content"),
):
    result = next((post for post in BLOG_POST if post["id"] == post_id), None)

    if result is None:
        return HTTPException(status_code=404, detail="Post not found")

    if not include_content:
        result = {key: value for key, value in result.items() if key != "content"}

    return result


@app.post("/posts", response_model=PostPublic, response_description="Post Created")
def create_post(post: PostCreate):
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "tags": [tag.model_dump() for tag in post.tags],
        "author": post.author.model_dump() if post.author else None,
    }

    BLOG_POST.append(new_post)

    return new_post


@app.put(
    "/posts/{post_id}",
    response_model=PostPublic,
    response_description="Post Updated",
    response_model_exclude_none=True,
)
def update_post(post_id: int, data: PostUpdate):
    for post in BLOG_POST:
        if post["id"] == post_id:
            payload = data.model_dump(exclude_unset=True)
            if "title" in payload:
                post["title"] = payload["title"]
            if "content" in payload:
                post["content"] = payload["content"]
            return post

    raise HTTPException(status_code=404, detail="Post not found")


@app.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int):
    for index, post in enumerate(BLOG_POST):
        if post["id"] == post_id:
            BLOG_POST.pop(index)
            return

    raise HTTPException(status_code=404, detail="Post not found")
