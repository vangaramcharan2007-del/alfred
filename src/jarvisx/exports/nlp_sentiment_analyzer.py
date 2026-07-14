"""
Genesis Omega NLP Sentiment Analyzer
Demonstrates a basic natural language processing pipeline using keyword scoring.
"""

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of a given string using a basic keyword scoring algorithm.
    """
    positive_keywords = {'good', 'great', 'excellent', 'amazing', 'love', 'fantastic', 'value'}
    negative_keywords = {'bad', 'terrible', 'awful', 'hate', 'poor', 'worst', 'issue'}
    
    words = text.lower().replace('.', '').replace('!', '').replace('?', '').split()
    
    score = 0
    for word in words:
        if word in positive_keywords:
            score += 1
        elif word in negative_keywords:
            score -= 1
            
    sentiment = "Neutral"
    if score > 0:
        sentiment = "Positive"
    elif score < 0:
        sentiment = "Negative"
        
    return {"text": text, "score": score, "sentiment": sentiment}

def execute_nlp_pipeline():
    # 1. Simulate a local dataset
    print("Initializing NLP Sentiment Engine...")
    dataset = [
        "This new feature is absolutely amazing and I love it!",
        "The recent update caused a terrible issue with my system.",
        "It works as expected. Nothing more to say.",
        "Great value for the price, excellent support.",
        "Worst experience ever, I hate this."
    ]
    
    # 2. Process the dataset
    print("Analyzing dataset...")
    results = []
    for comment in dataset:
        results.append(analyze_sentiment(comment))
        
    # 3. Print structured analytics report
    print("\n--- Sentiment Analytics Report ---")
    pos_count = sum(1 for r in results if r['sentiment'] == 'Positive')
    neg_count = sum(1 for r in results if r['sentiment'] == 'Negative')
    neu_count = sum(1 for r in results if r['sentiment'] == 'Neutral')
    
    print(f"Total Processed: {len(results)}")
    print(f"Positive: {pos_count} | Negative: {neg_count} | Neutral: {neu_count}\n")
    
    for idx, res in enumerate(results, 1):
        print(f"[{res['sentiment'].upper()}] (Score: {res['score']}) - \"{res['text']}\"")

if __name__ == "__main__":
    execute_nlp_pipeline()
