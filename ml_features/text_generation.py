import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import markovify

# Charger GPT-2 une seule fois
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")
model.eval()


def generate_gpt2_text(prompt, max_length=None, initial_max_length=50, extra_tokens=20, max_total_length=150):
    """
    Génère du texte depuis GPT-2 pré-entraîné en itérant jusqu'à obtenir une phrase terminée par une ponctuation.
    Si max_length est fourni, il sera utilisé comme valeur initiale.
    """
    if max_length is not None:
        initial_max_length = max_length
    # Génération initiale à partir du prompt
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            do_sample=True,
            temperature=0.8,
            top_k=50,
            top_p=0.95,
            max_length=initial_max_length,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Itération pour compléter le texte
    while generated_text and generated_text.strip()[-1] not in ".!?" \
          and len(tokenizer.encode(generated_text)) < max_total_length:
        new_length = len(tokenizer.encode(generated_text)) + extra_tokens
        with torch.no_grad():
            output_ids = model.generate(
                tokenizer.encode(generated_text, return_tensors="pt"),
                do_sample=True,
                temperature=0.8,
                top_k=50,
                top_p=0.95,
                max_length=new_length,
                no_repeat_ngram_size=2,
                early_stopping=True
            )
        new_generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        if new_generated_text == generated_text:
            break
        generated_text = new_generated_text

    return generated_text



def generate_markov_text(input_text, sentence_count=3):
    """
    Génération simple via Markovify.
    """
    if not input_text.strip():
        # Si l'utilisateur ne fournit rien
        return "Veuillez fournir un corpus pour la génération Markov."

    text_model = markovify.Text(input_text)
    lines = []
    for _ in range(sentence_count):
        line = text_model.make_sentence(tries=100)
        if line:
            lines.append(line)
    return "\n".join(lines)
