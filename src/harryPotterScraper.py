import requests
import bs4
import re
import pandas as pd
import tika
from tika import parser
from tqdm import tqdm


def form_bundle(character, statement, line, book):
    return {"character": character, "statement": statement, "line": line, "book": book}


def parse_first_book(transcript):
    lines = []
    for line in transcript.split("\n"):
        if line.strip() and "<div" not in line and "</div" not in line and line.strip() != "Scene:":
            lines.append(line.strip())

    all_dialogue = []
    for i, line in enumerate(lines):
        character_dialogue = re.findall(r"^([a-zA-Z0-9]+)[:\-](.+)$", line)
        if character_dialogue:
            for dialogue in character_dialogue:
                all_dialogue.append(form_bundle(dialogue[0].lower(), dialogue[1], i, 1))
        else:
            all_dialogue.append(form_bundle("environment", line, i, 1))
    return all_dialogue


def parse_second_book(transcript):
    all_dialogue = []
    attribute = ""
    statement = ""
    transcript = transcript.replace("\n\n", ":").replace("\n", " ")
    transcript = re.sub(r"THE CHAMBER OF SECRETS - Rev. [0-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,4}\s*[0-9]+\.?\s*(?:\([0-9]+\))?\s*[0-9]+", "", transcript)
    transcript = re.sub(r"[\s\t]+", " ", transcript)
    for line in transcript.split(":"):
        line = line.strip()
        if not line:
            continue

        if re.match(r"^(?:MRS?.\s?)?[^a-z!.']+$", line):
            if attribute and statement:
                line_number = len(all_dialogue)
                for character in attribute.split("/"):
                    all_dialogue.append(form_bundle(character, statement, line_number, 2))
            elif attribute and not statement and all_dialogue:
                all_dialogue[-1]["statement"] += f" {line}"
            attribute = re.sub(r"\(.+\)", "", line).lower().strip()
            attribute = attribute if attribute and not re.findall(r"[0-9]+|\s-\s", line) else "environment"
            for env_marker in ["scene", "montage", "dissolve", "closeup", "close-up", "chamber", "sees"]:
                attribute = "environment" if env_marker in attribute else attribute
            attribute = attribute.replace("justin-finch", "justin finch").replace("lucious", "lucius").replace("young ", "")
            attribute = "albus dumbledore" if attribute == "dumbledore" else attribute
            attribute = "tom riddle" if attribute == "riddle" else attribute
            attribute = "cornelius fudge" if attribute == "fudge" or attribute == "cornelius" else attribute
            statement = ""
        else:
            statement = line if not statement else f"{statement} {line}"
    return all_dialogue


def parse_third_book(transcript, book):
    all_dialogue = []
    transcript = re.sub(r"[\s\t]+", " ", transcript)
    for character, statement in re.findall(r"<b>([^a-z]+)</b>(.*?)<b>", transcript):
        character = character.strip().lower()
        statement = statement.strip().lower()
        if not statement or "<" in statement or not character or "(continued)" in character or "the end" in character:
            continue
        line_number = len(all_dialogue)
        if re.findall(r"[0-9)]+", character):
            character = "environment"
        for same_line_character in character.split("/"):
            all_dialogue.append(form_bundle(same_line_character, statement, line_number, book))
    return all_dialogue



def parse_transcript(transcript, book):
    all_dialogue = []
    transcript = transcript.strip()

    if book == 1:
        all_dialogue = parse_first_book(transcript)
    elif book == 2:
        all_dialogue = parse_second_book(transcript)
    else:
        all_dialogue = parse_third_book(transcript, book)
    return pd.DataFrame(all_dialogue)


def scrape_books():
    base = "http://www.hogwartsishere.com"
    all_books_url = f"{base}/library/book/7391"
    book_urls = {
        1: "http://www.hogwartsishere.com/library/book/7391/chapter/1",
        2: "http://www.hogwartsishere.com/library/book/7391/chapter/1",
        3: "http://nldslab.soe.ucsc.edu/charactercreator/film_corpus/film_20100519/all_imsdb_05_19_10/Harry-Potter-and-the-Prisoner-of-Azkaban.html"
    }
    books = {}
    for i, book_url in tqdm(book_urls.items()):
        bs = bs4.BeautifulSoup(requests.get(book_url).content, "html.parser")
        if "hogwartsishere.com" in book_url:
            transcript = str(bs.find("div", {"id": "wrapper"}).find("div", {"class": "font-size-16 roboto"})).replace("<br/>", "\n").replace("<br>", "\n")
        elif "nldslab.soe" in book_url:
            transcript = str(bs.find("td", {"class": "scrtext"}).find("pre")).replace("<br/>", "\n").replace("<br>", "\n")
        transcript_df = parse_transcript(transcript, i)
        transcript_df.to_csv(f"../corpora/harry_potter/harry_potter_{i}.csv", index=False)


if __name__ == "__main__":
    scrape_books()