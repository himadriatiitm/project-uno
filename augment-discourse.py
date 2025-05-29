import json
import os
from pathlib import Path
from html2text import HTML2Text
from typing import Any, Dict, List
import glob

# TOP_N_NON_ANSWER_RESPONSES = 5

corpus_collection = Path("discourse-corpuses")
os.makedirs(corpus_collection, exist_ok=True)

for path in glob.glob("discourse-posts/*"):
    print(f"working on {path}")
    filepath = Path(path)
    contents = json.loads(filepath.read_bytes())
    posts = contents["post_stream"]["posts"]
    if len(posts) == 0:
        exit(0)

    question: Dict[str, Any] = posts[0]
    responses: List[Dict[str, Any]] = posts[1:]

    found_answer = None

    for response in responses:
        if response["accepted_answer"]:
            found_answer = response

    if not found_answer:
        # responses.sort(key=lambda answer: answer["score"], reverse=True)
        # top_n_responses = responses[:TOP_N_NON_ANSWER_RESPONSES]
        top_n_responses = responses
    else:
        top_n_responses = [found_answer]

    textifier = HTML2Text()
    textifier.ignore_links = True
    textifier.bypass_tables = True

    dialogue = []
    for answer in top_n_responses:
        cooked = textifier.handle(answer["cooked"])
        dialogue.append("<url>{}</url><text>{}</text>".format(answer["post_url"], cooked.strip()))

    to_embed = "\n\n".join(dialogue)
    base = filepath.stem

    corpus_path = corpus_collection / f"discourse-{base}.md"
    corpus_path.write_text(to_embed)
