from transformers import BertTokenizer, BertForSequenceClassification

# Load FinBERT
tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def analyze_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    sentiment = outputs.logits.argmax(-1).item()
    labels = {0: "Negative", 1: "Neutral", 2: "Positive"}
    return labels[sentiment]

# Test the function
print(analyze_sentiment("Your recent purchase exceeded your budget."))
