import csv
import re

def export_tweets(src, dest):
    with open(src, "r") as tweet_reader:
        with open(dest, "w") as text_writer:
            for tweet in csv.DictReader(tweet_reader):
                tweeter = "Donald Trump"
                message = tweet["text"]
                retweet = re.findall(r"RT @([a-zA-Z0-9_-]+):(.+)", message)
                if retweet:
                    tweeter, message = retweet[0]
                text_writer.write(f"<|start_text|>{tweeter}: {message}<|end_text|>\n")

def concat_texts(dest, texts):
    with open(dest, "w") as dest_writer:
        for src in texts:
            with open(src, "r") as text_reader:
                dest_writer.write(text_reader.read()+"\n")

if __name__ == "__main__":
    # export_tweets("../corpora/trump_tweets.csv", "../corpora/trump.txt")
    concat_texts("../corpora/trump_csc.txt", ["../discord_bot/history/uafcsc.txt", "../corpora/trump.txt"])