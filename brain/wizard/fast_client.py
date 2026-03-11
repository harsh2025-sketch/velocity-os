import ollama

class FastBrain:
    def __init__(self, model="llama3:8b"):
        self.model = model
        print(f"⚡ Fast Brain: Using Ollama with {model}")

    def think(self, prompt, max_tokens=256):
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options={
                "num_predict": max_tokens,
                "temperature": 0.7
            }
        )
        return response['response']

if __name__ == "__main__":
    brain = FastBrain()
    print(brain.think("What is the capital of France?"))
