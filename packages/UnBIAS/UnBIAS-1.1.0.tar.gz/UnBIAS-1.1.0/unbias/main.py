import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, AutoModelForCausalLM, pipeline
import torch

def complete_sentence(text):
    """
    If the text ends mid-sentence, remove all words after the last full stop.
    """
    sentences = text.split(". ")
    if len(sentences) > 1 and not sentences[-1].endswith("."):
        return ". ".join(sentences[:-1]) + "."
    return text

class BiasPipeline:
    def __init__(self):
        # Load models and tokenizers once during initialization
        self.classifier_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-classifier")
        self.classifier_model = AutoModelForSequenceClassification.from_pretrained("newsmediabias/UnBIAS-classifier")

        self.ner_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-Named-entity")
        self.ner_model = AutoModelForTokenClassification.from_pretrained("newsmediabias/UnBIAS-Named-entity")

        self.debiaser_tokenizer = AutoTokenizer.from_pretrained("newsmediabias/UnBIAS-LLama2-Debiaser")
        self.debiaser_model = AutoModelForCausalLM.from_pretrained("newsmediabias/UnBIAS-LLama2-Debiaser")

        # Create pipelines once
        self.classifier = pipeline("text-classification", model=self.classifier_model, tokenizer=self.classifier_tokenizer)
        self.ner = pipeline("ner", model=self.ner_model, tokenizer=self.ner_tokenizer)
    def clean_text(self, text):
        # Replace multiple spaces with a single space
        cleaned_text = ' '.join(text.split())
        return cleaned_text

    def process(self, texts):
        classification_results = self.classifier(texts)
        ner_results = self.ner(texts)
        
        debiaser_results = []
        for text in texts:
            val_prompt = f"""[INST] You are a text debiasing bot, you take as input a text and you output its debiased version, the debiased version should not differentiate among gender, race, age groups and must not use toxic or bad language, without any extra outputs.\n{text} [/INST]"""
            model_input = self.debiaser_tokenizer(val_prompt, return_tensors="pt", truncation=True)
            
            self.debiaser_model.eval()
            with torch.no_grad():
                output = self.debiaser_model.generate(**model_input, max_length=150, repetition_penalty=1.2, temperature=0.8)
            debiased_text = self.debiaser_tokenizer.decode(output[0], skip_special_tokens=True).replace(val_prompt, '').strip()
            
            # Ensure the debiased text ends with a complete sentence and is cleaned
            debiased_text = self.clean_text(complete_sentence(debiased_text))
            
            debiaser_results.append(debiased_text)
        
        return classification_results, ner_results, debiaser_results


    def pretty_print(self, texts, classification_results, ner_results, debiaser_results):
          for i in range(len(classification_results)):
              print("Original Text:")
              print(texts[i])  # Access the text directly from the input texts
              print("="*50)
              print(f"Classification Label: {classification_results[i]['label']}")
              print(f"Classification Score: {classification_results[i]['score']:.4f}")
              biased_words = [entry['word'] for entry in ner_results[i] if entry['entity'] == 'Biased']
              print("Biased Words Detected:")
              for word in biased_words:
                  print(f"- {word}")
              print("="*50)
              print("Debiased Text:")
              print(debiaser_results[i])
              print("="*50)

def results_to_dataframe(texts, classification_results, ner_results, debiaser_results):
    data = {
        'Original Text': texts,  # Use the input texts directly
        'Classification Label': [result['label'] for result in classification_results],
        'Classification Score': [result['score'] for result in classification_results],
        'Biased Words': [[entry['word'] for entry in ner if entry['entity'] == 'Biased'] for ner in ner_results],
        'Debiased Text': debiaser_results
    }
    df = pd.DataFrame(data)
    return df


