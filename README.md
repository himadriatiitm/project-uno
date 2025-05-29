```sh
shopt -s globstar; for f in tools-in-data-science-public/**/*.md; do cp "$f" "corpuses/sanand0-$(basename "$f")"; done
llm embed-multi project-uno --model 3-small --store --format nl chunks.json
```
