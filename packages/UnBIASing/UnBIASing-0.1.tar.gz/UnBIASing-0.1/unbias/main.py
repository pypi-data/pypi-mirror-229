import pandas as pd
from transformers import (AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, 
                          AutoModelForSeq2SeqLM, GPT2Tokenizer, GPT2LMHeadModel, DistilBertTokenizer, 
                          DistilBertForSequenceClassification, pipeline)
import torch

def complete_sentence(text):
    """If the text ends mid-sentence, remove all words after the last full stop."""
    sentences = text.split(". ")
    if len(sentences) > 1 and not sentences[-1].endswith("."):
        return ". ".join(sentences[:-1]) + "."
    return text

class BiasPipeline:
    def __init__(self):
        # Load models and tokenizers
        self.classifier_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-classifier")
        self.classifier_model = AutoModelForSequenceClassification.from_pretrained("newsmediabias/UnBIAS-classifier")

        self.ner_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-Named-entity")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("newsmediabias/UnBIAS-Named-entity")

        self.debiaser_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-Debiaser")
        self.debiaser_model = AutoModelForSeq2SeqLM.from_pretrained("newsmediabias/UnBIAS-Debiaser")

        self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2-medium")
        self.gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2-medium")

        self.sentiment_tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')


    def classifier(self, texts):
        """Classify texts using the bias classifier."""
        classifier_pipe = pipeline('sentiment-analysis', model=self.classifier_model, tokenizer=self.classifier_tokenizer)
        return classifier_pipe(texts)

    def ner(self, texts):
        """Get named entities from texts using the NER model."""
        ner_pipe = pipeline('ner', model=self.ner_model, tokenizer=self.ner_tokenizer)
        return ner_pipe(texts)

    def get_sentiment_score(self, text):
        """Get sentiment score. 0: negative, 1: neutral, 2: positive."""
        inputs = self.sentiment_tokenizer.encode(text, return_tensors='pt', truncation=True)
        with torch.no_grad():
            outputs = self.sentiment_model(inputs)[0]
        prediction = torch.argmax(outputs, dim=1).item()
        return prediction

    def ensemble_debias_text(self, text):
        debiased_texts = []

        # Using the T5 model
        t5_input = self.debiaser_tokenizer.encode(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            t5_output = self.debiaser_model.generate(t5_input, max_length=150)
        t5_debiased = self.debiaser_tokenizer.decode(t5_output[0], skip_special_tokens=True)
        debiased_texts.append(t5_debiased)

        # Using the GPT-2 model
        gpt2_input = self.gpt2_tokenizer.encode(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            gpt2_output = self.gpt2_model.generate(gpt2_input, max_length=150)
        gpt2_debiased = self.gpt2_tokenizer.decode(gpt2_output[0], skip_special_tokens=True)
        debiased_texts.append(gpt2_debiased)

        # Selection logic
        sentiments = [self.get_sentiment_score(dt) for dt in debiased_texts]
        if sentiments[0] == sentiments[1]:
            # If both texts have the same sentiment, pick the one closest in length
            selected_text = sorted(debiased_texts, key=lambda x: abs(len(x) - len(text)))[0]
        else:
            # Pick the text with a more positive sentiment
            selected_text = debiased_texts[sentiments.index(max(sentiments))]

        return selected_text

    def clean_text(self, text):
        """Replace multiple spaces with a single space and remove certain predefined strings."""
        cleaned_text = ' '.join(text.split())
        cleaned_text = cleaned_text.replace("You are a text debiasing bot.", "").strip()
        cleaned_text = cleaned_text.replace("Produce a debiased version of the following text without including these instructions:", "").strip()
        return cleaned_text

    def process(self, texts):
        """Classify, detect NER and debias texts."""
        classification_results = self.classifier(texts)
        ner_results = self.ner(texts)

        debiaser_results = []
        for text in texts:
            debiased_text = self.ensemble_debias_text(text)
            debiased_text = self.clean_text(complete_sentence(debiased_text))
            debiaser_results.append(debiased_text)

        return classification_results, ner_results, debiaser_results

    def pretty_print(self, texts, classification_results, ner_results, debiaser_results):
        """Pretty print the results."""
        for i in range(len(texts)):
            print("Original Text:")
            print(texts[i])
            print("=" * 50)
            print(f"Classification Label: {classification_results[i]['label']}")
            print(f"Classification Score: {classification_results[i]['score']:.4f}")
            biased_words = [entry['word'] for entry in ner_results[i] if entry['entity'] == 'Biased']
            print("Biased Words Detected:")
            for word in biased_words:
                print(f"- {word}")
            print("=" * 50)
            print("Debiased Text:")
            print(debiaser_results[i])
            print("=" * 50)


def results_to_dataframe(texts, classification_results, ner_results, debiaser_results):
    data = {
        'Original Text': texts,
        'Classification Label': [result['label'] for result in classification_results],
        'Classification Score': [result['score'] for result in classification_results],
        'Biased Words': [[entry['word'] for entry in ner if entry['entity'] == 'Biased'] for ner in ner_results],
        'Debiased Text': debiaser_results
    }
    df = pd.DataFrame(data)
    return df
