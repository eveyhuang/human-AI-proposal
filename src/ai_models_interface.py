"""
Unified interface for multiple AI models to generate research ideas based on proposals.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# AI Model imports
import openai
from google import genai
import anthropic
# X.AI SDK imports
from xai_sdk import Client
from xai_sdk.chat import user, system
from dashscope import Generation
# LangChain for NCEMS API (llama-4-scout)
from langchain_community.chat_models import ChatLiteLLM

# Import prompt templates
from prompt_templates import PromptManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Container for AI model responses"""
    model_name: str
    session_id: str
    generated_ideas: str
    timestamp: str
    metadata: Dict[str, Any]

class AIModelsInterface:
    """Unified interface for multiple AI models"""
    
    def __init__(
        self,
        config_path: str = "human-AI-proposal/.env",
        prompt_template: str = "standard_extension",
        override_env: bool = False,
    ):
        """Initialize the interface with API keys from config file"""
        self.load_config(config_path, override_env=override_env)
        self.setup_models()
        self.prompt_manager = PromptManager()
        self.current_template = prompt_template
        
    def load_config(self, config_path: str, override_env: bool = False):
        """
        Load API keys from environment or config file.

        By default, existing environment variables take precedence.
        Set override_env=True (recommended for Jupyter) to force values from `config_path`
        (e.g., a local `.env`) to overwrite already-set environment variables.
        """

        # If a config file exists, optionally inject it into os.environ first.
        # This avoids the common "stale key in the kernel env" issue.
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                for raw_line in f:
                    line = raw_line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if override_env or key not in os.environ:
                        os.environ[key] = value

        # Read final values from environment (possibly updated above)
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.xai_key = os.getenv("XAI_API_KEY")
        self.ncems_api_key = os.getenv("NCEMS_API_KEY")
        self.ncems_api_url = os.getenv("NCEMS_API_URL")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    def setup_models(self):
        """Initialize AI model clients"""
        self.models = {}
        
        # OpenAI (GPT)
        if self.openai_key:
            openai.api_key = self.openai_key
            self.models['gpt-5.2'] = self._call_openai
            logger.info("OpenAI GPT-4 initialized")
        
        # Google Gemini
        if self.google_key:
            self.gemini_client = genai.Client(api_key=self.google_key)
            self.models['gemini-3-pro-preview'] = self._call_gemini
            logger.info("Google Gemini initialized")
        
        # Anthropic Claude
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            self.models['claude-opus-4-5'] = self._call_claude
            logger.info("Anthropic Claude initialized")
        
        # X.AI Grok (uses xai_sdk)
        if self.xai_key:
            self.xai_client = Client(
                api_key=self.xai_key,
                timeout=3600  # Longer timeout for reasoning models
            )
            self.models['grok-4'] = self._call_grok
            logger.info("X.AI Grok-4 initialized")
        
        # # NCEMS API models (via LiteLLM)
        # if self.ncems_api_key and self.ncems_api_url:
        #     # Llama-4-Scout
        #     self.llama_client = ChatLiteLLM(
        #         model="litellm_proxy/js2/llama-4-scout",
        #         api_key=self.ncems_api_key,
        #         api_base=self.ncems_api_url
        #     )
        #     self.models['llama-4-scout'] = self._call_llama
        #     logger.info("NCEMS Llama-4-Scout initialized")

        #     # Qwen-2.5
        #     self.qwen_client = ChatLiteLLM(
        #         model="litellm_proxy/anvilgpt/qwen2.5:7b",
        #         api_key=self.ncems_api_key,
        #         api_base=self.ncems_api_url
        #     )
        #     self.models['qwen-2.5'] = self._call_qwen
        #     logger.info("NCEMS Qwen-2.5 initialized")

        #     # DeepSeek-R1
        #     self.deepseek_client = ChatLiteLLM(
        #         model="litellm_proxy/js2/DeepSeek-R1",
        #         api_key=self.ncems_api_key,
        #         api_base=self.ncems_api_url
        #     )
        #     self.models['deepseek-r1'] = self._call_deepseek
        #     logger.info("NCEMS DeepSeek-R1 initialized")
    
    def _call_openai(self, prompt: str, **kwargs) -> str:
        """Call OpenAI GPT-4"""
        try:
            client = openai.OpenAI(api_key=self.openai_key)
            
            # GPT-5.2 requires max_completion_tokens instead of max_tokens
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0),
                max_completion_tokens=kwargs.get('max_completion_tokens', kwargs.get('max_tokens', 16000))
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"Error: {str(e)}"
    
    def _call_gemini(self, prompt: str, **kwargs) -> str:
        """Call Google Gemini"""
        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=[prompt],
                config={
                    'response_mime_type': 'application/json',
                    'temperature': kwargs.get('temperature', 0)
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"Error: {str(e)}"
    
    def _call_claude(self, prompt: str, **kwargs) -> str:
        """Call Anthropic Claude Sonnet 4.5"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-opus-4-5",  # Official model ID for Claude Sonnet 4.5
                max_tokens=kwargs.get('max_tokens', 16000),  # Required parameter; max is 8192
                temperature=kwargs.get('temperature', 0),
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return f"Error: {str(e)}"
    
    # def _call_grok(self, prompt: str, **kwargs) -> str:
    #     """Call X.AI Grok-4 using xai_sdk"""
    #     try:
    #         # Create a new chat session
    #         chat = self.xai_client.chat.create(model="grok-4")
            
    #         # Add system message
    #         chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
            
    #         # Add user prompt
    #         chat.append(user(prompt))
            
    #         # Sample response
    #         response = chat.sample()
            
    #         return response.content
    #     except Exception as e:
    #         logger.error(f"X.AI Grok-4 error: {e}")
    #         return f"Error: {str(e)}"
    
    # def _call_llama(self, prompt: str, **kwargs) -> str:
    #     """Call NCEMS llama-4-scout via LiteLLM"""
    #     try:
    #         # LangChain's ChatLiteLLM uses the invoke method
    #         response = self.llama_client.invoke(prompt)
            
    #         # Extract content from response
    #         if hasattr(response, 'content'):
    #             return response.content
    #         else:
    #             return str(response)
    #     except Exception as e:
    #         logger.error(f"NCEMS Llama-4-Scout error: {e}")
    #         return f"Error: {str(e)}"
    
    # def _call_qwen(self, prompt: str, **kwargs) -> str:
    #     """Call NCEMS Qwen-2.5 via LiteLLM"""
    #     try:
    #         # LangChain's ChatLiteLLM uses the invoke method
    #         response = self.qwen_client.invoke(prompt)
            
    #         # Extract content from response
    #         if hasattr(response, 'content'):
    #             return response.content
    #         else:
    #             return str(response)
    #     except Exception as e:
    #         logger.error(f"NCEMS Qwen-2.5 error: {e}")
    #         return f"Error: {str(e)}"
    
    # def _call_deepseek(self, prompt: str, **kwargs) -> str:
    #     """Call NCEMS DeepSeek-R1 via LiteLLM"""
    #     try:
    #         # LangChain's ChatLiteLLM uses the invoke method
    #         response = self.deepseek_client.invoke(prompt)
            
    #         # Extract content from response
    #         if hasattr(response, 'content'):
    #             return response.content
    #         else:
    #             return str(response)
    #     except Exception as e:
    #         logger.error(f"NCEMS DeepSeek-R1 error: {e}")
    #         return f"Error: {str(e)}"
    
    # def _call_qwen(self, prompt: str, **kwargs) -> str:
    #     """Call Qwen via DashScope"""
    #     try:
    #         response = Generation.call(
    #             model='qwen-turbo',
    #             prompt=prompt,
    #             api_key=self.dashscope_key,
    #             temperature=kwargs.get('temperature', 0.7),
    #             max_tokens=kwargs.get('max_tokens', 2000)
    #         )
    #         return response.output.text
    #     except Exception as e:
    #         logger.error(f"Qwen error: {e}")
    #         return f"Error: {str(e)}"
    
    def generate_content(self, prompt: str, model_name: str = 'gemini-2.5-pro', **kwargs) -> str:
        """
        Generate content using a specific model with a given prompt.
        This is a simpler method for direct prompt-to-response generation.
        
        Args:
            prompt: The prompt text to send to the model
            model_name: The model to use (default: gemini-2.5-pro)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            The generated text response
        """
        if model_name not in self.models:
            available_models = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not available. Available models: {available_models}")
        
        # Call the model directly
        response = self.models[model_name](prompt, **kwargs)
        
        return response
    
    def generate_research_ideas(self, research_call: str, model_name: str, 
                               prompt_template: str = None, **kwargs) -> AIResponse:
        """Generate research ideas based on the research call using a specific model"""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not available")
        
        # Idea generation uses generate_ideas_baseline (prompt_templates.py)
        template_name = prompt_template or self.current_template
        template_name_to_use = (
            template_name if template_name == 'generate_ideas_baseline' else 'generate_ideas_baseline'
        )
        prompt = self.prompt_manager.format_prompt(template_name_to_use, {'research_call': research_call})
        
        # Call the model
        raw_response = self.models[model_name](prompt, **kwargs)
        
        # Try to parse JSON response
        parsed_ideas = self._parse_json_response(raw_response)
        
        # Create response object
        response = AIResponse(
            model_name=model_name,
            session_id='research_call_session',  # Since we're working with research call
            generated_ideas=parsed_ideas,
            timestamp=datetime.now().isoformat(),
            metadata={
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens', 16000),
                'prompt_template': template_name,
                'research_call': research_call,
                'raw_response': raw_response,
                'parsed_successfully': parsed_ideas is not None
            }
        )
        
        return response
    
    def _parse_json_response(self, raw_response: str) -> str:
        """Parse JSON response from AI model, return structured data or raw response if parsing fails"""
        logger.info(f"Raw response length: {len(raw_response)} characters")
        logger.info(f"Raw response preview: {raw_response[:200]}...")
        
        try:
            # Try to extract JSON from the response
            response_text = raw_response.strip()
            
            # Look for JSON object in the response
            if response_text.startswith('{') and response_text.endswith('}'):
                parsed_data = json.loads(response_text)
                return json.dumps(parsed_data, indent=2, ensure_ascii=False)
            else:
                # Try to find the first complete JSON object
                start_idx = response_text.find('{')
                if start_idx != -1:
                    # Find the matching closing brace for the first JSON object
                    brace_count = 0
                    end_idx = start_idx
                    for i, char in enumerate(response_text[start_idx:], start_idx):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i
                                break
                    
                    if end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx+1]
                        parsed_data = json.loads(json_str)
                        return json.dumps(parsed_data, indent=2, ensure_ascii=False)
                
                # Return raw response if no JSON found
                logger.warning("No valid JSON found in response, returning raw text")
                return raw_response
                    
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return raw_response
        except Exception as e:
            logger.error(f"Unexpected error parsing response: {e}")
            return raw_response
    
    async def generate_ideas_for_all_models(self, research_call: str, **kwargs) -> List[AIResponse]:
        """Generate research ideas using all available models"""
        tasks = []
        for model_name in self.models.keys():
            task = asyncio.create_task(
                self._async_generate_ideas(research_call, model_name, **kwargs)
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid responses
        valid_responses = []
        for response in responses:
            if isinstance(response, AIResponse):
                valid_responses.append(response)
            else:
                logger.error(f"Error generating response: {response}")
        
        return valid_responses
    
    async def _async_generate_ideas(self, research_call: str, model_name: str, **kwargs) -> AIResponse:
        """Async wrapper for idea generation"""
        return self.generate_research_ideas(research_call, model_name, **kwargs)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(self.models.keys())
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available prompt templates"""
        return self.prompt_manager.list_templates()
    
    def set_prompt_template(self, template_name: str):
        """Set the default prompt template"""
        if template_name not in self.prompt_manager.get_all_templates():
            raise ValueError(f"Template '{template_name}' not found. Available: {list(self.prompt_manager.get_all_templates().keys())}")
        self.current_template = template_name
        logger.info(f"Set prompt template to: {template_name}")
    
    def compare_templates(self, proposal: Dict[str, Any], template_names: List[str] = None) -> Dict[str, str]:
        """Compare different prompt templates for the same proposal"""
        if template_names is None:
            template_names = list(self.prompt_manager.get_all_templates().keys())
        
        return self.prompt_manager.compare_templates(template_names, proposal)
    
    async def generate_ideas_with_multiple_templates(self, proposal: Dict[str, Any], 
                                                   model_name: str, 
                                                   template_names: List[str] = None,
                                                   **kwargs) -> List[AIResponse]:
        """Generate ideas using multiple prompt templates for comparison"""
        if template_names is None:
            template_names = list(self.prompt_manager.get_all_templates().keys())
        
        responses = []
        for template_name in template_names:
            try:
                response = self.generate_research_ideas(
                    proposal, model_name, prompt_template=template_name, **kwargs
                )
                responses.append(response)
            except Exception as e:
                logger.error(f"Error with template {template_name}: {e}")
        
        return responses
