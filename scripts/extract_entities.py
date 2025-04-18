#!/usr/bin/env python3
import os, glob, json
import tensorflow as tf
from transformers import BertTokenizerFast, TFBertForTokenClassification

def load_model(model_name="dslim/bert-base-NER"):
    tokenizer = BertTokenizerFast.from_pretrained(model_name)
    model     = TFBertForTokenClassification.from_pretrained(model_name)
    return tokenizer, model

def predict_entities(tokenizer, model, text):
    tokens = tokenizer(text,
                       return_offsets_mapping=True,
                       return_tensors="tf",
                       truncation=True)
    outputs = model(tokens["input_ids"])[0]
    preds = tf.math.argmax(outputs, axis=-1).numpy()[0]
    labels = [model.config.id2label[p] for p in preds]
    offset_mapping = tokens.pop("offset_mapping").numpy()[0]
    # collect only non-[PAD], non-[CLS]/[SEP] tokens with a label
    ents = []
    for lab, (start, end), tok in zip(labels, offset_mapping, tokenizer.convert_ids_to_tokens(tokens["input_ids"][0])):
        if lab != "O" and tok not in ["[CLS]","[SEP]"]:
            ents.append({
                "entity": lab,
                "text": text[start:end],
                "start": int(start),
                "end": int(end)
            })
    return ents

def main(input_dir, output_dir, model_name="dslim/bert-base-NER"):
    tokenizer, model = load_model(model_name)
    os.makedirs(output_dir, exist_ok=True)
    for jf in glob.glob(os.path.join(input_dir, "*.json")):
        data = json.load(open(jf))
        ents = predict_entities(tokenizer, model, data["text"])
        data["entities"] = ents
        out_path = os.path.join(output_dir, os.path.basename(jf))
        with open(out_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import fire
    fire.Fire(main)
