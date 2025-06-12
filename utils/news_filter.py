from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

sentiment_model_name = "wonrax/phobert-base-vietnamese-sentiment"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)

toxicity_model_name = "naot97/vietnamese-toxicity-detection_1"
toxicity_tokenizer = AutoTokenizer.from_pretrained(toxicity_model_name)
toxicity_model = AutoModelForSequenceClassification.from_pretrained(toxicity_model_name)

def analyze_sentiment(text):
    inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = sentiment_model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    return probabilities.argmax().item()  # 0: NEG, 1: POS, 2: NEU

def detect_toxicity(text):
    inputs = toxicity_tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = toxicity_model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    return probabilities[0][1].item() > 0.5  # 1: Toxic, 0: Non-toxic