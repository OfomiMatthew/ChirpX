"""
AI Service Module for ChirpX
Provides AI-powered features using Groq API
"""

import os
from groq import Groq
from typing import Dict, List, Optional
import json
import re

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq AI client"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in your environment or .env file")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and capable model
    
    def _call_groq(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Make a call to Groq API"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            print(f"Groq API Error: {str(e)}")
            return None
    
    def moderate_content(self, content: str) -> Dict:
        """
        Check if content is appropriate and doesn't violate community guidelines
        Returns: {
            'is_safe': bool,
            'reason': str (if not safe),
            'categories': list (types of violations)
        }
        """
        prompt = f"""Analyze the following text for inappropriate content. Check for:
- Hate speech, harassment, or bullying
- Violence or graphic content
- Sexual or adult content
- Spam or misleading information
- Personal attacks or threats

Text to analyze: "{content}"

Respond ONLY in JSON format:
{{
    "is_safe": true/false,
    "reason": "brief explanation if not safe, empty string if safe",
    "categories": ["list", "of", "violations"] or []
}}"""

        messages = [
            {"role": "system", "content": "You are a content moderation assistant. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.3, max_tokens=200)
        
        if response:
            try:
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Default safe response if API fails
        return {"is_safe": True, "reason": "", "categories": []}
    
    def generate_reply_suggestions(self, chirp_content: str, num_suggestions: int = 3) -> List[str]:
        """
        Generate smart reply suggestions for a chirp
        Returns list of suggested replies
        """
        prompt = f"""Generate {num_suggestions} brief, engaging reply suggestions (max 100 characters each) for this social media post:

"{chirp_content}"

Requirements:
- Keep replies natural and conversational
- Match the tone of the original post
- Make them diverse (supportive, question, funny/light)
- Keep under 100 characters each

Respond with ONLY the suggestions, one per line, numbered 1-{num_suggestions}."""

        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates engaging social media replies."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.8, max_tokens=300)
        
        if response:
            # Parse numbered suggestions
            suggestions = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove numbering (1., 2., etc.)
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', line)
                # Remove quotes if present
                cleaned = cleaned.strip('"\'')
                if cleaned and len(cleaned) <= 150:
                    suggestions.append(cleaned)
            return suggestions[:num_suggestions]
        
        return []
    
    def analyze_sentiment(self, content: str) -> Dict:
        """
        Analyze the sentiment of a chirp
        Returns: {
            'sentiment': 'positive'/'negative'/'neutral',
            'score': float (-1 to 1),
            'emotions': list of detected emotions
        }
        """
        prompt = f"""Analyze the sentiment and emotions in this text:

"{content}"

Respond ONLY in JSON format:
{{
    "sentiment": "positive" or "negative" or "neutral",
    "score": number between -1 (very negative) and 1 (very positive),
    "emotions": ["list", "of", "primary", "emotions"]
}}

Common emotions: joy, sadness, anger, fear, surprise, love, excitement, frustration, hope"""

        messages = [
            {"role": "system", "content": "You are a sentiment analysis assistant. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.3, max_tokens=200)
        
        if response:
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {"sentiment": "neutral", "score": 0, "emotions": []}
    
    def suggest_hashtags(self, content: str, num_tags: int = 5) -> List[str]:
        """
        Suggest relevant hashtags for a chirp
        Returns list of hashtag suggestions (without #)
        """
        prompt = f"""Generate {num_tags} relevant hashtags for this social media post:

"{content}"

Requirements:
- Make them relevant to the content
- Keep them concise (1-2 words)
- Mix popular and specific tags
- Return ONLY hashtags, one per line
- Do NOT include the # symbol

Example format:
Technology
Innovation
AI"""

        messages = [
            {"role": "system", "content": "You are a social media expert specializing in hashtag recommendations."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.7, max_tokens=150)
        
        if response:
            tags = []
            for line in response.split('\n'):
                line = line.strip()
                # Remove # if present, remove numbering
                cleaned = re.sub(r'^[\d\.\)#\s]+', '', line)
                cleaned = cleaned.strip('"\'')
                if cleaned and len(cleaned) <= 30:
                    # Convert to camelCase or remove spaces
                    tag = ''.join(word.capitalize() for word in cleaned.split())
                    tags.append(tag)
            return tags[:num_tags]
        
        return []
    
    def enhance_content(self, content: str) -> Dict:
        """
        Suggest improvements to make the chirp more engaging
        Returns: {
            'improved_content': str,
            'suggestions': list of improvement tips
        }
        """
        prompt = f"""Improve this social media post to make it more engaging while keeping the original message:

Original: "{content}"

Requirements:
- Keep it under 280 characters
- Maintain the original tone and message
- Make it more engaging and clear
- Fix any grammar issues

Respond in JSON format:
{{
    "improved_content": "the improved version",
    "suggestions": ["tip1", "tip2", "tip3"]
}}"""

        messages = [
            {"role": "system", "content": "You are a social media writing coach. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.7, max_tokens=400)
        
        if response:
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {"improved_content": content, "suggestions": []}
    
    def detect_spam(self, content: str, user_history: Optional[Dict] = None) -> Dict:
        """
        Detect if content is spam or suspicious
        Returns: {
            'is_spam': bool,
            'confidence': float (0-1),
            'reason': str
        }
        """
        history_context = ""
        if user_history:
            history_context = f"\nUser has posted {user_history.get('post_count', 0)} times today."
        
        prompt = f"""Analyze if this content is spam or suspicious:

"{content}"{history_context}

Check for:
- Excessive links or promotional content
- Repetitive messages
- Suspicious URLs
- Get-rich-quick schemes
- Phishing attempts
- Too many hashtags (spam indicator)

Respond ONLY in JSON format:
{{
    "is_spam": true/false,
    "confidence": number between 0 and 1,
    "reason": "brief explanation"
}}"""

        messages = [
            {"role": "system", "content": "You are a spam detection assistant. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.2, max_tokens=200)
        
        if response:
            try:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return {"is_spam": False, "confidence": 0.0, "reason": ""}
    
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """
        Summarize a conversation thread
        messages: list of dicts with 'username' and 'content'
        """
        conversation = "\n".join([f"{msg['username']}: {msg['content']}" for msg in messages])
        
        prompt = f"""Summarize this conversation in 1-2 sentences:

{conversation}

Keep the summary concise and capture the main points."""

        system_message = [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(system_message, temperature=0.5, max_tokens=150)
        return response if response else "Unable to generate summary."
    
    def generate_trending_topics(self, chirps: List[str], top_n: int = 5) -> List[Dict]:
        """
        Analyze chirps to identify trending topics
        Returns list of topics with relevance scores
        """
        # Combine recent chirps
        combined = "\n".join(chirps[:50])  # Limit to 50 recent chirps
        
        prompt = f"""Analyze these social media posts and identify the top {top_n} trending topics or themes:

{combined}

Respond ONLY in JSON format as an array:
[
    {{"topic": "topic name", "relevance": 0.95}},
    {{"topic": "topic name", "relevance": 0.87}}
]

Relevance should be between 0 and 1."""

        messages = [
            {"role": "system", "content": "You are a trend analysis assistant. Respond only with valid JSON array."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_groq(messages, temperature=0.5, max_tokens=300)
        
        if response:
            try:
                # Extract JSON array from response
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        return []
    
    def generate_image_with_groq(self, prompt: str) -> Dict:
        """
        Generate an image using Groq API to create ASCII art and render it as an image
        Returns: {
            'success': bool,
            'image_path': str,
            'enhanced_prompt': str,
            'ascii_art': str,
            'error': str (if failed)
        }
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Use Groq to create ASCII art
            messages = [
                {"role": "system", "content": "You are a creative AI artist that generates detailed ASCII art. Create beautiful, detailed ASCII art based on the user's description. Use standard ASCII characters to create recognizable images."},
                {"role": "user", "content": f"Create detailed ASCII art for: {prompt}\n\nMake it visually appealing and recognizable. Use at least 15-20 lines to make it detailed."}
            ]
            
            ascii_art = self._call_groq(messages, temperature=0.9, max_tokens=1000)
            
            if ascii_art:
                import time
                timestamp = int(time.time())
                
                # Save ASCII art as text file
                txt_filename = f"ascii_art_{timestamp}.txt"
                txt_filepath = os.path.join('static', 'uploads', txt_filename)
                os.makedirs(os.path.dirname(txt_filepath), exist_ok=True)
                
                with open(txt_filepath, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                
                # Render ASCII art as an image
                img_filename = f"ai_generated_{timestamp}.png"
                img_filepath = os.path.join('static', 'uploads', img_filename)
                
                # Calculate image size based on ASCII art
                lines = ascii_art.split('\n')
                max_width = max(len(line) for line in lines) if lines else 80
                height = len(lines)
                
                # Create image with dark theme
                font_size = 12
                char_width = 7
                char_height = 14
                
                img_width = max_width * char_width + 40
                img_height = height * char_height + 40
                
                # Create image with dark background
                image = Image.new('RGB', (img_width, img_height), color='#1a1a1a')
                draw = ImageDraw.Draw(image)
                
                # Try to use a monospace font
                try:
                    font = ImageFont.truetype("consola.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("cour.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                
                # Draw ASCII art in green/cyan color
                y_offset = 20
                for line in lines:
                    draw.text((20, y_offset), line, fill='#00ff88', font=font)
                    y_offset += char_height
                
                # Save the image
                image.save(img_filepath)
                
                return {
                    'success': True,
                    'image_path': f'uploads/{img_filename}',
                    'txt_path': f'uploads/{txt_filename}',
                    'enhanced_prompt': prompt,
                    'ascii_art': ascii_art,
                    'type': 'ascii'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate ASCII art'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image generation error: {str(e)}'
            }
    
    def generate_image(self, prompt: str) -> Dict:
        """
        Generate an image using AI based on text description
        Uses Groq's image generation capabilities or generates a placeholder
        Returns: {
            'success': bool,
            'image_url': str,
            'error': str (if failed)
        }
        """
        try:
            # Note: Groq primarily focuses on text generation
            # For actual image generation, you'd need to integrate services like:
            # - DALL-E (OpenAI)
            # - Stable Diffusion
            # - Midjourney API
            
            # For demonstration, we'll create a text-based response
            # In production, integrate with actual image generation API
            
            # Using a placeholder service (replicate, stability.ai, etc.)
            # For now, return a placeholder or use Groq to enhance the prompt
            
            enhanced_prompt = self._enhance_image_prompt(prompt)
            
            # In a real implementation, call image generation API here
            # For example: response = stability_ai.generate(enhanced_prompt)
            
            # Placeholder response - you should integrate actual image generation
            return {
                'success': False,
                'error': 'Image generation requires additional API setup (DALL-E, Stable Diffusion, etc.)',
                'enhanced_prompt': enhanced_prompt,
                'suggestion': 'Please upload an image instead, or integrate an image generation API like DALL-E or Stable Diffusion.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image generation error: {str(e)}'
            }
    
    def _enhance_image_prompt(self, prompt: str) -> str:
        """Use AI to enhance the image generation prompt"""
        messages = [
            {"role": "system", "content": "You are an AI art prompt engineer. Enhance user prompts for image generation."},
            {"role": "user", "content": f"Enhance this image generation prompt to be more detailed and artistic: {prompt}\n\nProvide only the enhanced prompt, nothing else."}
        ]
        
        response = self._call_groq(messages, temperature=0.8, max_tokens=150)
        return response if response else prompt


# Singleton instance
_ai_service_instance = None

def get_ai_service() -> AIService:
    """Get or create AI service instance"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIService()
    return _ai_service_instance
