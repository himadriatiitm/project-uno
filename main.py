import sqlite_utils
import llm
import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI

class Request(BaseModel):
    question: str
    image: Optional[str]


class Response(BaseModel):
    text: str
    url: str

def between_tags(string: str, rope: str) -> str:
    rope_start = f'<{rope}>'
    rope_end = f'</{rope}>'
    start = string.index(rope_start) + len(rope_start)
    end = string.index(rope_end)
    return string[start:end]

db = sqlite_utils.Database("embeddings.db")
model = llm.get_model("gpt-4o-mini")
model.key = os.environ["OPENAI_API_KEY"]
collection = llm.Collection("project-uno", db, model_id=model)

app = FastAPI()

@app.post("/api/")
async def post_root(request: Request) -> Response:
    notes = ""
    similar = collection.similar(request.question, number=5)
    for id, entry in enumerate(similar):
        name, _fragment = entry.id.split("#")
        context = Path(name).read_text()
        notes += "\n" + context

    response = model.prompt(
        f"""
{notes}

Answer only from the above notes.
Cite verbatim from notes in <text></text> tags.
Cite the url above the text block for your chosen answer in <url></url> tags.
If the answer is not in the context, answer "I don't know."

{request.question}
""",
        # TODO:
        # attachments=[
        #     llm.Attachment(content=b'somebinaryblob')
        # ]
    ).text()
    url = between_tags(response, "url")
    text = between_tags(response, "text")
    return Response(text=text, url=url)
