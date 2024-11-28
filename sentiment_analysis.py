from transformers import BertTokenizer, BertForSequenceClassification
import torch

tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def analyze_sentiment(transaction_description):
    inputs = tokenizer(transaction_description, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    sentiment = outputs.logits.argmax(-1).item()
    labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return labels[sentiment]

# Test the function
description = "You were charged $50 for a subscription."
print(f"Sentiment: {analyze_sentiment(description)}")
