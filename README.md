The discourse scraping script is `scraper.py`.

# Getting started

- Update your discourse cookies in `cookies.json`. The example cookies have expired.
- I use fish shell on Linux but you might need to source `.venv/bin/activate`.
- Export your OPENAI_API_KEY as an environment variable in your shell.

``` sh
rm ./discourse-posts ./corpuses ./chunks.json -rf
git clone https://github.com/sanand0/tools-in-data-science-public --depth 1
uv venv .venv
source .venv/bin/activate.fish
python scraper.py
python augment.py
bash generate-chunks.sh
llm embed-multi project-uno --model 3-small \
  --store --format nl chunks.json \
  -d embeddings.db
fastapi dev main.py
```

> [!NOTE]
>
> lavafroth is my work account. You might notice commits from it here. Sorry about that.
