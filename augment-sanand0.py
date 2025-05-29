from pathlib import Path
import os

p = Path('./tools-in-data-science-public/')
g = p.glob('**/*.md')

for gg in g:
    relpath = Path(os.path.relpath(gg, p))
    name = str(relpath).removesuffix(".md")
    url = f"https://tds.s-anand.net/#/{name}"
    text = gg.read_text()
    content = f'<url>{url}</url><text>{text}</text>'
    dest = Path("./corpuses") / ("sanand0-" + str(relpath).replace('/', '-'))
    dest.write_text(content)
    print(url)
