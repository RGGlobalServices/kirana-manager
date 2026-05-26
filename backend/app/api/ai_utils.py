import os
from openai import OpenAI
from PIL import Image
import json
import io
import base64

# Initialize OpenAI client to connect to NVIDIA API
client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.environ.get("NVIDIA_API_KEY", "") 
)

def extract_product_details(image_bytes: bytes):
    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_bytes))
    
    # Convert image to base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    prompt = """
    Analyze this product image (likely a grocery item) and extract the following details in JSON format:
    - name: The brand and product name (e.g., "Fortune Sunlite Refined Sunflower Oil")
    - category: Purely the category (e.g., "Oil", "Pulses", "Soap", "Snack")
    - mrp: The Maximum Retail Price as a number (omit currency symbols)
    - selling_price: Expected selling price (usually 2-5% less than MRP if not specified)
    - base_unit: One of [Unit, Kg, Gram, Bottle, Box, Ltr]
    - weight_volume: The weight or volume (e.g., "1 L", "500 g")

    Only return valid JSON. If a field is missing, use null.
    """
    
    try:
        response = client.chat.completions.create(
            model="meta/llama-3.2-11b-vision-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1024,
            temperature=0.2,
        )
        
        text = response.choices[0].message.content.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()
            
        return json.loads(text)
    except Exception as e:
        print(f"OCR Error: {e}")
        return None
