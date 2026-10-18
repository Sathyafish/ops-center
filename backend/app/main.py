from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import authenticate_user, create_access_token, get_current_user
from app.config import settings
from app.graph.neo4j_client import close_driver
from app.rag.graph_agent import run_query as run_rag_query


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from app.config import settings

    print(
        f"Ops Center API: llm={settings.llm_provider} embed={settings.embedding_provider} "
        f"ollama={settings.ollama_base_url}"
    )
    yield
    close_driver()


app = FastAPI(title="Ops Center GraphRAG", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, str]


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    mode: str = Field(default="auto", pattern="^(auto|graph|vector)$")


class QueryResponse(BaseModel):
    answer: str
    route: str
    graph_context: str
    vector_context: str
    citations: dict


@app.get("/health")
def health() -> dict[str, str]:
    from app.config import settings

    return {
        "status": "ok",
        "llm_provider": settings.llm_provider,
        "embedding_provider": settings.embedding_provider,
        "ollama_model": settings.ollama_model if settings.llm_provider == "ollama" else "",
    }


@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    user = authenticate_user(body.username, body.password)
    if user is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(user["username"])
    return LoginResponse(access_token=token, user=user)


@app.post("/query", response_model=QueryResponse)
def query(
    body: QueryRequest,
    user: dict = Depends(get_current_user),
) -> QueryResponse:
    _ = user
    result = run_rag_query(body.question, mode=body.mode)  # type: ignore[arg-type]
    return QueryResponse(**result)
