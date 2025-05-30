import sqlite_utils
import llm
import os
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import base64


class Request(BaseModel):
    question: str
    image: Optional[str] = Field(None, description="Image for additional context.")


class Link(BaseModel):
    text: str
    url: str


class Response(BaseModel):
    answer: str
    links: List[Link]


def between_tags(string: str, rope: str) -> str:
    rope_start = f"<{rope}>"
    rope_end = f"</{rope}>"
    start = string.index(rope_start) + len(rope_start)
    end = string.index(rope_end)
    return string[start:end]


db = sqlite_utils.Database("embeddings.db")
model = llm.get_model("gpt-4o-mini")
model.key = os.environ["OPENAI_API_KEY"]
collection = llm.Collection("project-uno", db, model_id=model)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def root():
    return {'hello': 'world'}

@app.post("/api/")
async def post_root(request: Request) -> Response:
    attachments = []
    if request.image:
        attachments.append(llm.Attachment(content=base64.b64decode(request.image)))

    links = []
    notes = ""
    similar = collection.similar(request.question, number=3)
    for id, entry in enumerate(similar):
        name, _fragment = entry.id.split("#")
        context = Path(name).read_text()
        notes += "\n" + context
        response = model.prompt(
            f"""
{context}

Answer only from the above notes.
Cite verbatim from notes in <text></text> tags.
Cite the url above the text block for your chosen answer in <url></url> tags.
If the answer is not in the context, answer "<unknown>"

{request.question}
""",
            attachments=attachments,
        ).text()
        if "<unknown>" in response:
            continue

        url = between_tags(response, "url")
        text = between_tags(response, "text")
        links.append(Link(text=text, url=url))

    response = model.prompt(
        f"""
{notes}

Answer only from the above notes.
Write your final answer in <answer></answer> tags.
If the answer is not in the context, respond with <answer>I don't know</answer>.

{request.question}
"""
    ).text()
    answer = between_tags(response, "answer")
    return Response(answer=answer, links=links)
