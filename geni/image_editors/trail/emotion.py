from transformers import pipeline

# Load the pre-trained emotion detection pipeline
emotion_detector = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", return_all_scores=True)

# Function to detect emotions in text
def detect_emotion(self,text):
    results = emotion_detector(text)
    # Extract scores and sort by confidence
    sorted_emotions = sorted(results[0], key=lambda x: x['score'], reverse=True)
    return sorted_emotions

# Test the function
test_text = "I am so excited to see what the future holds!"
emotions = detect_emotion(test_text)

# Display results
print(f"Detected emotions for the text: '{test_text}'")
for emotion in emotions:
    print(f"{emotion['label']}: {emotion['score']:.4f}")
