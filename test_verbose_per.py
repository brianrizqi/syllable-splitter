from HybridSyllableSplitter import HybridSyllableSplitter
splitter = HybridSyllableSplitter()
words = ['memperalat', 'memperistri', 'peroleh']
for w in words:
    print(f"--- {w} ---")
    prefix, detected_root, suffix, lemmatized_root = splitter.morphology.analyze_with_lemmatizer(w)
    print(f"Morph: prefix='{prefix}', detected='{detected_root}', suffix='{suffix}', lemmatized='{lemmatized_root}'")
    base_prefix, infix = splitter.morphology.decompose_prefix(prefix)
    print(f"Decompose: base='{base_prefix}', infix='{infix}'")
    print(f"Result: {splitter.split_syllables(w)}")
