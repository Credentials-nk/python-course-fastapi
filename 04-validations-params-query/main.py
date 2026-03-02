from math import ceil
from typing import List, Literal, Optional, Union

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(title="Mini Blog")


BLOG_POST = [
    {
        "id": 1,
        "title": "Hello from FastAPI",
        "content": "My first post with FastAPI",
    },
    {
        "id": 2,
        "title": "Hey there",
        "content": "Good look everywhere",
        "tags": [{"name": "general"}],
    },
    {
        "id": 3,
        "title": "NL2SQL at City Hall",
        "content": "First step to let the mayor query data using natural language",
        "tags": [{"name": "sql"}, {"name": "ai"}],
    },
    {
        "id": 4,
        "title": "Python Best Practices",
        "content": "Learning the best practices for writing clean and efficient Python code in your applications",
        "tags": [{"name": "python"}, {"name": "clean-code"}, {"name": "backend"}],
    },
    {
        "id": 5,
        "title": "Web Development Tips",
        "content": "Essential tips and tricks for building modern web applications with FastAPI and Python",
        "tags": [{"name": "fastapi"}, {"name": "python"}],
    },
    {
        "id": 6,
        "title": "Database Design Guide",
        "content": "Understanding how to design efficient databases for your web applications and data management",
        "tags": [{"name": "database"}, {"name": "sql"}],
    },
    {
        "id": 7,
        "title": "API Security Matters",
        "content": "Implementing security best practices in your API to protect user data and prevent vulnerabilities",
        "tags": [{"name": "security"}, {"name": "api"}, {"name": "backend"}],
    },
    {
        "id": 8,
        "title": "Testing Strategies",
        "content": "Comprehensive guide to testing your FastAPI applications with unit tests and integration tests",
        "tags": [{"name": "testing"}, {"name": "fastapi"}],
    },
    {
        "id": 9,
        "title": "Docker Containerization",
        "content": "Learn how to containerize your FastAPI applications using Docker for better deployment",
        "tags": [{"name": "docker"}, {"name": "devops"}],
    },
    {
        "id": 10,
        "title": "Performance Optimization",
        "content": "Tips for optimizing your FastAPI application performance and reducing response times",
        "tags": [{"name": "performance"}, {"name": "fastapi"}, {"name": "backend"}],
    },
    {
        "id": 11,
        "title": "Authentication Methods",
        "content": "Different authentication methods implementation in FastAPI including JWT and OAuth2 tokens",
        "tags": [{"name": "security"}, {"name": "jwt"}],
    },
    {
        "id": 12,
        "title": "Error Handling Patterns",
        "content": "Best practices for handling errors gracefully in your FastAPI applications and APIs",
        "tags": [{"name": "backend"}, {"name": "python"}],
    },
    {
        "id": 13,
        "title": "Async Programming",
        "content": "Understanding asynchronous programming in Python and how to leverage it in FastAPI",
        "tags": [{"name": "python"}, {"name": "async"}],
    },
    {
        "id": 14,
        "title": "Microservices Architecture",
        "content": "Building scalable microservices using FastAPI and deploying them effectively",
        "tags": [{"name": "architecture"}, {"name": "devops"}, {"name": "fastapi"}],
    },
    {
        "id": 15,
        "title": "GraphQL Integration",
        "content": "Integrating GraphQL with FastAPI to provide flexible query capabilities for your clients",
        "tags": [{"name": "graphql"}, {"name": "api"}],
    },
    {
        "id": 16,
        "title": "Real-time Updates",
        "content": "Implementing real-time features using WebSockets with FastAPI for live data updates",
    },
    {
        "id": 17,
        "title": "Monitoring and Logging",
        "content": "Setting up comprehensive monitoring and logging for your FastAPI applications in production",
        "tags": [{"name": "devops"}, {"name": "backend"}],
    },
    {
        "id": 18,
        "title": "Documentation Generation",
        "content": "Automatically generating API documentation with FastAPI and Swagger UI integration",
        "tags": [{"name": "fastapi"}, {"name": "api"}],
    },
    {
        "id": 19,
        "title": "Deployment Strategies",
        "content": "Different strategies for deploying FastAPI applications to production environments",
        "tags": [{"name": "devops"}, {"name": "docker"}, {"name": "architecture"}],
    },
    {
        "id": 20,
        "title": "Community and Resources",
        "content": "Discovering the FastAPI community resources and staying updated with latest developments",
        "tags": [{"name": "general"}],
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
    tags: Optional[List[Tag]] = Field(default_factory=list)
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
    tags: Optional[List[Tag]] = Field(default_factory=list)  # []

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


class PaginatedPost(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool
    order_by: Literal["id", "title"] | None
    direction: Literal["asc", "desc"] | None
    search: str | None
    # limit: int
    # offset: int
    items: List[PostPublic]


@app.get("/")
def home():
    return {"message": "Welcome to my blog by Niko"}


@app.get("/posts", response_model=PaginatedPost)
def list_posts(
    text: Optional[str] = Query(
        default=None,
        description="Deprecated parameter use query instead",
        deprecated=True,
    ),
    query: Optional[str] = Query(
        default=None,
        description="Test for search by title",
        alias="search",
        min_length=3,
        max_length=10,
        # Acepta: letras a-z, A-Z, dígitos, guión bajo (_),
        # y vocales con tilde (á é í ó ú Á É Í Ó Ú Ü ü)
        # No permite espacios, símbolos ni caracteres especiales
        # Debe tener al menos 1 carácter del set definido
        pattern=r"^[\w\sáéíóúÁÉÍÓÚÜü-]+$",
    ),
    # limit: int = Query(10, ge=1, le=50, description="Results of (1-50)"),
    # offset: int = Query(
    #     0, ge=0, description="Number of items to skip before listing results"
    # ),
    per_page: int = Query(10, ge=1, le=50, description="Results of (1-50)"),
    page: int = Query(1, ge=1, description="Number of page (>=1)"),
    order_by: Literal["id", "title"] = Query("id", description="Input to order"),
    direction: Literal["asc", "desc"] = Query("asc", description="Order direction"),
):
    results = BLOG_POST

    query = query or text

    if query:
        results = [post for post in results if query.lower() in post["title"].lower()]

    total = len(results)
    total_pages = ceil(total / per_page) if total > 0 else 0
    current_page = min(page, total_pages) if total_pages > 0 else 1

    results = sorted(
        results, key=lambda post: post[order_by], reverse=(direction == "desc")
    )

    start = (current_page - 1) * per_page
    items = [PostPublic(**post) for post in results[start : start + per_page]]

    return PaginatedPost(
        page=current_page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        has_prev=current_page > 1,
        has_next=current_page < total_pages,
        order_by=order_by,
        direction=direction,
        search=query,
        items=items,
    )


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


@app.get("/post/by-tags", response_model=List[PostPublic])
def filter_by_tags(
    tags: List[str] = Query(
        ...,
        min_length=2,
        description="One or more tags",
        example="Example: ?tags=python&tags=fastapi",
    ),
):
    tags_lower = [tag.lower() for tag in tags]

    return [
        post
        for post in BLOG_POST
        if any(tag["name"].lower() in tags_lower for tag in post.get("tags", []))
    ]


@app.post("/posts", response_model=PostPublic, response_description="Post Created")
def create_post(post: PostCreate):
    new_id = (BLOG_POST[-1]["id"] + 1) if BLOG_POST else 1

    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "tags": [tag.model_dump() for tag in (post.tags or [])],
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
