import requests
import bs4
import re
import pandas as pd
import tika
from tika import parser


def parse_transcript(transcript):
    all_dialogue = []
    transcript = transcript.strip()
    for i, line in enumerate([line for line in transcript.split("\n") if line.strip() and "<div" not in line and "</div" not in line and line.strip() != "Scene:"]):
        character_dialogue = re.findall(r"^([a-zA-Z0-9]+):(.+)$", line)
        if character_dialogue:
            for dialogue in character_dialogue:
                all_dialogue.append({
                    "character": dialogue[0].lower(),
                    "statement": dialogue[1],
                    "line": i
                })
        else:
            all_dialogue.append({
                "character": "environment",
                "statement": line,
                "line": i
            })
    return pd.DataFrame(all_dialogue)


def scrape_books():
    base = "http://www.hogwartsishere.com"
    all_books_url = f"{base}/library/book/7391"
    books = {}
    for i in range(1,8):
        book_url = f"{all_books_url}/chapter/{i}"
        bs = bs4.BeautifulSoup(requests.get(book_url).content, "html.parser")
        transcript = str(bs.find("div", {"id": "wrapper"}).find("div", {"class": "font-size-16 roboto"})).replace("<br/>", "\n")
        transcript_df = parse_transcript(transcript)
        transcript_df.to_csv(f"../corpora/harry_potter/harry_potter_{i}.csv", index=False)

if __name__ == "__main__":
    scrape_books()