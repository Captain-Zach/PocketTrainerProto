import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

class LLMHandler:
    def __init__(self, model_path):
        """
        Initializes the LLM handler by loading the tokenizer and model from a local path.
        """
        self.model_path = model_path
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self._load_model()

    def _load_model(self):
        """
        Loads the tokenizer and model from the local filesystem.
        """
        if not os.path.isdir(self.model_path):
            print(f"Error: Model path does not exist: {self.model_path}")
            return

        try:
            print(f"Loading tokenizer from {self.model_path}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            print("Tokenizer loaded successfully.")

            print(f"Loading model from {self.model_path}...")
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.bfloat16,
                device_map=self.device,
            )
            print("Model loaded successfully.")

        except Exception as e:
            print(f"Error loading model: {e}")
            self.tokenizer = None
            self.model = None

    def generate_response(self, prompt, max_new_tokens=150):
        """
        Generates a response from the LLM based on a given prompt.
        """
        if not self.model or not self.tokenizer:
            return "Model is not loaded. Please check for errors during initialization."

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        try:
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95
            )
            response_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # The prompt is often included in the response, so we remove it.
            if response_text.startswith(prompt):
                response_text = response_text[len(prompt):].lstrip()
            return response_text
        except Exception as e:
            return f"Error during text generation: {e}"

if __name__ == '__main__':
    # This is for testing the LLMHandler directly
    print("Performing a test run of the LLMHandler...")
    
    # Construct the path to the local model directory
    local_model_dir = os.path.join(os.path.dirname(__file__), "local_models", "gemma-3n-E2B-it")
    
    handler = LLMHandler(model_path=local_model_dir)
    if handler.model:
        test_prompt = "What is the capital of France?"
        print(f"Test Prompt: {test_prompt}")
        response = handler.generate_response(test_prompt)
        print(f"LLM Response: {response}")
    else:
        print("LLM Handler initialization failed. Cannot run test.")

