import torch
print(torch.backends.mps.is_available())
print(torch.backends.mps.is_built())

import torch
from transformers import BertTokenizer, BertModel

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')
model.to(device)

text = "Hello, how are you?"
inputs = tokenizer(text, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)

print(outputs.last_hidden_state.shape)