import sys
import os
try:
    from airllm import AutoModel
except ImportError:
    print("CRITICAL: AirLLM not installed. Run 'pip install airllm'")
    sys.exit(1)

class DeepBrain:
    def __init__(self):
        print("🧠 Deep Brain: Initializing AirLLM (70B Layer-Swapping)...")
        # Ensure we use 4-bit compression to fit in RAM
        self.model = AutoModel.from_pretrained(
            "garage-bAInd/Platypus2-70B-instruct", 
            compression="4bit",
            device_map="auto"
        )

    def think(self, prompt, max_tokens=512):
        """
        Executes high-IQ inference. Warning: High Latency.
        """
        input_tokens = self.model.tokenizer(prompt, return_tensors="pt")
        
        # Generate with AirLLM optimization
        output = self.model.generate(
            input_tokens.input_ids,
            max_new_tokens=max_tokens,
            use_cache=True,
            return_dict_in_generate=True
        )
        
        return self.model.tokenizer.decode(output.sequences[0])

if __name__ == "__main__":
    # Test block
    brain = DeepBrain()
    print(brain.think("Explain Quantum Computing in one sentence."))
