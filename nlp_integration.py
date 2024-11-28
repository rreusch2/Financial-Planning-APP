from transformers import BertTokenizer, BertForSequenceClassification

# Load FinBERT
tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def analyze_transaction_sentiment(description):
    inputs = tokenizer(description, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    sentiment = outputs.logits.argmax(-1).item()
    labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return labels[sentiment]
