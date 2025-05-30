### Getting started

Update your discourse cookies in `cookies.json`

```sh
rm ./discourse-posts ./discourse-corpuses ./corpuses -rf
uv venv .venv
source .venv/bin/activate.fish # or change this to activate, I use fish
python project-scraper.py
python augment-discourse.py
python augment-sanand0.py
bash generate-chunks.sh
llm embed-multi project-uno --model 3-small \
  --store --format nl chunks.json \
  -d embeddings.db
fastapi dev main.py
```

> [NOTE]: lavafroth is my work account. You might notice commits from it here. Sorry about that.

