from HybridSyllableSplitter import HybridSyllableSplitter
splitter = HybridSyllableSplitter()
words = ['dipakai', 'diberhentikan', 'ditempati', 'ditinggal']
for w in words:
    print(f"--- {w} ---")
    prefix, detected_root, suffix, lemmatized_root, internal_infix = splitter.morphology.analyze_with_lemmatizer(w)
    print(f"Morph: prefix='{prefix}', detected='{detected_root}', suffix='{suffix}', lemmatized='{lemmatized_root}'")
    print(f"Result: {splitter.split_syllables(w)}")
