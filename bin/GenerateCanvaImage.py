import requests
import json
import base64
import os
from typing import Optional, Dict, Any

class CanvaAPIClient:
    """
    Client for interacting with Canva's API to generate custom images based on templates.
    """
    def __init__(self, api_key: str):
        """
        Initialize the Canva API client.
        
        Args:
            api_key: Your Canva API key
        """
        self.api_key = api_key
        self.base_url = "https://api.canva.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def list_templates(self) -> Dict[str, Any]:
        """
        List available templates in your Canva account.
        
        Returns:
            Response containing template information
        """
        endpoint = f"{self.base_url}/templates"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """
        Get details about a specific template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Template details
        """
        endpoint = f"{self.base_url}/templates/{template_id}"
        response = requests.get(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string of the image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def generate_image(self, 
                      template_id: str, 
                      text_values: Dict[str, str],
                      background_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a custom image based on a template.
        
        Args:
            template_id: ID of the template to use
            text_values: Dictionary mapping text element IDs to custom text values
            background_image_path: Path to background image file (optional)
            
        Returns:
            Response containing the URL to the generated image
        """
        payload = {
            "templateId": template_id,
            "elements": {
                "text": text_values
            }
        }
        
        # Add background image if provided
        if background_image_path:
            background_image_base64 = self.encode_image_to_base64(background_image_path)
            payload["elements"]["images"] = {
                "background": {
                    "content": background_image_base64,
                    "encoding": "base64"
                }
            }
        
        endpoint = f"{self.base_url}/designs/generate"
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
    
    def download_image(self, image_url: str, output_path: str) -> str:
        """
        Download a generated image.
        
        Args:
            image_url: URL of the generated image
            output_path: Path where the image will be saved
            
        Returns:
            Path to the downloaded image
        """
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return output_path


def main():
    # Replace with your actual API key
    api_key = "your_canva_api_key"
    
    # Initialize the client
    canva_client = CanvaAPIClient(api_key)
    
    # Example: List available templates
    templates = canva_client.list_templates()
    print(f"Available templates: {json.dumps(templates, indent=2)}")
    
    # Sample template ID (replace with actual template ID from your account)
    template_id = "ABCD1234"
    
    # Get template details to identify element IDs
    template_details = canva_client.get_template_details(template_id)
    print(f"Template details: {json.dumps(template_details, indent=2)}")
    
    # Custom text values (map element IDs to your custom text)
    text_values = {
        "heading": "My Custom Heading",
        "subheading": "This is a custom subheading",
        "body": "This is the main content of my design."
    }
    
    # Path to your background image
    background_image = "path/to/your/background.jpg"
    
    # Generate custom image
    result = canva_client.generate_image(
        template_id=template_id,
        text_values=text_values,
        background_image_path=background_image
    )
    
    # Download the generated image
    if "imageUrl" in result:
        output_path = "generated_image.jpg"
        canva_client.download_image(result["imageUrl"], output_path)
        print(f"Image successfully generated and saved to {output_path}")
    else:
        print(f"Failed to generate image: {result}")


if __name__ == "__main__":
    main()