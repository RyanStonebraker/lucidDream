import sys
import os
import contextlib
with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
    import gpt_2_simple as gpt2
    import tensorflow as tf
    tf.logging.set_verbosity(tf.logging.ERROR)
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
    import logging
    logging.getLogger('tensorflow').setLevel(logging.FATAL)

import random
import pandas as pd
import numpy as np
import math
import re

from nltk.corpus import stopwords
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split


class LucidDream:
    def __init__(
        self,
        characters=["trump", "harry", "ron", "hermione", "snape", "albus dumbledore", "tom riddle", "hagrid", "environment"],
        response_length=30,
        run_name="small_uafcsc_better"
    ):
        self.characters = characters
        self.sess = gpt2.start_tf_sess()
        self.response_length=response_length
        self.run_name=run_name

        self.init_classifier()


    def init_classifier(self):
        isear_df = pd.read_csv("../corpora/isear.csv", header=None)
        isear_df.columns = ["emotion", "text", ""]
        isear_df = isear_df.drop([""], axis=1)

        cleaned_text = [self.clean_text(text) for text in isear_df["text"].tolist()]

        count_vectorizer = CountVectorizer()
        training_counts = count_vectorizer.fit_transform(cleaned_text)
        tfidf_transformer = TfidfTransformer()
        bag_of_words = count_vectorizer.transform(cleaned_text)
        tfidf_transformer.fit(bag_of_words)

        self.classifier = Pipeline([
                ('vect', count_vectorizer), 
                ('tfidf', tfidf_transformer),
                ('clf', SGDClassifier(loss="log", 
                                    penalty='l1',
                                    random_state=1
                                    ))
            ])

        X_train, X_test, Y_train, Y_test = train_test_split(cleaned_text, isear_df["emotion"].tolist(), test_size=0.3, random_state=1)
        self.classifier.fit(X_train, Y_train)


    def clean_text(self, content):
        content = content.lower().strip()
        content = re.sub(r"[^a-zA-Z]", " ", str(content))
        content = re.sub(r"[\s\t\n]+", " ", content)
        tokens = [word for word in content.split() if word and word not in stopwords.words("english")]
        cleaned_text = " ".join(tokens)
        return cleaned_text


    def generate_holistic_model_response(self, conversation, character, filtered=True):
        common_letters = "tiiiiiiainosriiiitainosiatwbmtikgdpr"
        seed = "\n".join([f"{sentence[0].strip()}: {sentence[1].strip()}" for sentence in conversation[-30::-1]]) + f"\n{character}:" if not self.run_name.startswith("new") else f"<|start_text|>{character}: "
        # print(f"Seed: {seed}")
        gpt2.reset_session(self.sess)
        self.sess = gpt2.start_tf_sess()
        gpt2.load_gpt2(self.sess, run_name=self.run_name)
        response = gpt2.generate(
            self.sess,
            length=self.response_length,
            temperature=0.73,
            prefix=seed,# + random.choice(common_letters + common_letters.upper()),
            nsamples=1,
            batch_size=1,
            run_name=self.run_name,
            return_as_list=True
        )[0]
        print("RAW:\n", response[len(seed):])
        response = response[len(seed):].strip()
        # print("R", response)
        
        # if len(response.split(":")) > 1:
        #     response = response.split(":")[0].strip()
        # filtered_words = " ".join(re.findall(r".+?[.?!]", response)).strip()

        if "<|end_text|>" in response:
            output = re.findall(r"(.+?)<\|end_text\|>", response)
            return output[0] if output else response.replace("<|start_text|>", "").strip()
        else:
            return response
        # print("R", response, len(re.split(r"[\s\t\n]", response)) - len(re.split(r"[\s\t\n]", filtered_words)))

        # return response

        # filtered_response = filtered_words if len(re.split(r"[\s\t\n]", response)) - len(re.split(r"[\s\t\n]", filtered_words)) <= 3 and filtered_words.strip() else response
        # print("FR", filtered_response)
        split_response = response.split(":")
        formatted = []
        for res in split_response:
            if res.endswith(character):
                formatted.append(res[:res.rfind(character)])
            else:
                formatted.append(res)
                break
        return "\n".join(formatted)
        # return filtered_response
        # return re.split(r"[a-z A-Z0-9]+:", response)[0].strip().split("\n")[0] if filtered else response


    def start_conversation(
        self,
        conversation=[],
        filtered=True
    ):
        # with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
        character = random.choice(self.characters)
        response = self.generate_holistic_model_response(conversation, character, filtered=filtered)
        return response


    def get_class_probs(self, data):
        prob_spread = self.classifier.predict_proba([data]).tolist()[0]
        probabilities = pd.DataFrame({"class": self.classifier.classes_, "probability": prob_spread})
        probabilities = probabilities.sort_values(by="probability", ascending=False)
        probabilities = probabilities.set_index("class").T.reset_index()
        del probabilities["index"]
        probabilities["predicted"] = self.classifier.predict([data])
        return probabilities

    
    def get_emotional_profile(self, character, guild):
        history = {"character": [], "text": []}
        with open (f"history/{guild}.txt", "r") as history_reader:
            raw_lines = history_reader.read().split("<|end_text|>")
            for line in raw_lines:
                line = line.replace("<|start_text|>", "").strip()
                history["character"].append(line[:line.find(":")])
                history["text"].append(line[line.find(":")+1:].strip())
        df = pd.DataFrame(history)


        emotion_breakdown = pd.concat([self.get_class_probs(row.text) for i, row in df[df.character == character].iterrows()], sort=False)

        character_df = pd.DataFrame(emotion_breakdown.mean()).T
        character_df.index.name = character
        character_df = character_df.T.rename(columns={0:"percent"}).sort_values(by="percent", ascending=False)
        return character_df


if __name__ == "__main__":
    # import gpt_2_simple as gpt2
    # sess = gpt2.start_tf_sess()
    # gpt2.finetune(
    #     sess,
    #     "../corpora/harry_potter/small_text.txt",
    #     model_name="124M",
    #     steps=100,
    #     restore_from="fresh",
    #     run_name="small_text_small_run1",
    #     print_every=10,
    #     sample_every=200,
    #     save_every=100
    # )


    lucidDream = LucidDream(
        characters=["harry", "ron", "hermione", "snape", "albus dumbledore", "tom riddle", "hagrid", "environment"],
        response_length=50
    )

    print(lucidDream.start_conversation([("harry", "this is a test.")], filtered=True))