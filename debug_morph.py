from MorphologicalAnalyzer import MorphologicalAnalyzer

analyzer = MorphologicalAnalyzer()
words = ["dikokang", "memerah", "menguatkan", "mengkerut", "gelegar"]

for w in words:
    print(f"Word: {w}")
    print(f"  Analyze: {analyzer.analyze(w)}")
    print(f"  Lemmatize: {analyzer.lemmatizer.lemmatize(w, lang='id') if analyzer.lemmatizer else 'N/A'}")
    print(f"  AnalyzeWithLemmatizer: {analyzer.analyze_with_lemmatizer(w)}")
    print("-" * 20)
