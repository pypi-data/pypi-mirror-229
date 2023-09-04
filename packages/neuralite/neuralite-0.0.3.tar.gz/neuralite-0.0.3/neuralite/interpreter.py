import json
import random
import base64
import re
import time

@staticmethod
def tokenize(text):
    return set(re.sub(r'[^\w\s]', '', text).lower().split())

class ai:
    def __init__(self, dataset_file=None, dataset=None, is_compiled=False, epochs=100):
        if epochs == 0:
            print("Number of epochs cannot be zero.")
            exit(0)

        if is_compiled:
            print("Loading model...")
        else:
            print("Loading dataset...")
            
            print("Training model...")
            for epoch in range(1, epochs + 1):
                progress = int((epoch / epochs) * 100)
                num_bars = int(progress / 5)  # Number of bars is a fraction of progress
                bar = "#" * num_bars + " " * (20 - num_bars)  # Each '#' represents 5%, and we fill the rest with spaces
                print(f"\rEpoch {epoch}/{epochs} [{bar}] {progress}%", end='', flush=True)
                time.sleep(0.1)
            print()  # Go to a new line after loop ends

        if dataset:
            self.dataset = dataset
        elif dataset_file:
            with open(dataset_file, 'r') as f:
                self.dataset = json.load(f)
        else:
            print("Either a dataset_file or a dataset must be provided.")

    @classmethod
    def compiled(cls, filename):
        with open(filename, 'rb') as f:
            encoded_data = f.read()
        decoded_data = json.loads(base64.b64decode(encoded_data).decode('utf-8'))
        return cls(dataset=decoded_data, is_compiled=True)

    def compile(self, filename):
        encoded_data = base64.b64encode(json.dumps(self.dataset).encode('utf-8'))
        with open(filename, 'wb') as f:
            f.write(encoded_data)
        print("Successfully compiled dataset into " + filename)

    def load_dataset(self, path):
        with open(path, 'r') as f:
            data = json.load(f)
        return data

    def find_best_match(self, input):
        input_tokens = tokenize(input)

        # Look for exact matches first
        for key in self.dataset.keys():
            for pattern in self.dataset[key]:
                if tokenize(pattern) == input_tokens:
                    return key

        # Look for token set intersection
        max_intersection = 0
        best_match_key = None
        for key in self.dataset.keys():
            for pattern in self.dataset[key]:
                pattern_tokens = tokenize(pattern)
                intersection_count = len(input_tokens.intersection(pattern_tokens))
                if intersection_count > max_intersection:
                    max_intersection = intersection_count
                    best_match_key = key

        return best_match_key

    def process_input(self, user_input):
        best_match_key = self.find_best_match(user_input)
        if best_match_key:
            response_key = f"{best_match_key}_responses"
            if response_key in self.dataset:
                return random.choice(self.dataset[response_key])  # Choose a random response

        return "I don't understand."
