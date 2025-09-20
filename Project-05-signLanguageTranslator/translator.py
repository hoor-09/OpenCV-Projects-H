import cv2
import numpy as np
from hand_utils import HandDetector
from letters import LETTER_MAPPINGS, WORD_DATABASE, WORD_MATCH_THRESHOLD

class SignLanguageTranslator:
    def __init__(self):
        self.detector = HandDetector()
        self.current_letters = []
        self.translation_history = []
        self.word_buffer = ""
        self.space_timer = 0

    def _predict_word(self):
        # Compare current letters to word database
        for word, data in WORD_DATABASE.items():
            match_score = self._calculate_match_score(data["letters"])
            WORD_DATABASE[word]["score"] = match_score
        
        # Get best match
        best_match = max(WORD_DATABASE.items(), key=lambda x: x[1]["score"])
        if best_match[1]["score"] >= WORD_MATCH_THRESHOLD:
            return best_match[0]
        return None

    def _calculate_match_score(self, target_letters):
        # Calculate how closely current letters match a word
        if len(self.current_letters) != len(target_letters):
            return 0
        
        correct = sum(1 for a, b in zip(self.current_letters, target_letters) if a == b)
        return correct / len(target_letters)

    def translate_frame(self, frame):
        results = self.detector.detect_hands(frame)
        
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                self.detector.mp_draw.draw_landmarks(
                    frame, landmarks, self.detector.mp_hands.HAND_CONNECTIONS
                )
                
                letter = self.detector.classify_gesture(landmarks.landmark)
                if letter and (not self.current_letters or letter != self.current_letters[-1]):
                    self.current_letters.append(letter)
                    if letter == " ":
                        self.word_buffer += " "
                    else:
                        self.word_buffer += letter

        # Word prediction
        predicted_word = self._predict_word()
        display_text = f"Letters: {' '.join(self.current_letters)}"
        
        if predicted_word:
            display_text += f"\nPredicted: {predicted_word}"
            # Reset after prediction
            if len(self.current_letters) >= len(WORD_DATABASE[predicted_word]["letters"]):
                self.current_letters = []
                self.word_buffer = ""

        # Display
        y_offset = 50
        for line in display_text.split('\n'):
            cv2.putText(frame, line, (30, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            y_offset += 30

        return frame

def main():
    translator = SignLanguageTranslator()
    cap = cv2.VideoCapture(0)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.flip(frame, 1)
        frame = translator.translate_frame(frame)
        
        cv2.imshow("ASL Translator", frame)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()