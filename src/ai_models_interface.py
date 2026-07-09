"""
Unified interface for multiple AI models to generate research ideas based on proposals.
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
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

STUDY_MODEL_REGISTRY: Dict[str, Dict[str, str]] = {
    'gpt-5.5': {
        'provider': 'openai',
        'provider_model_id': 'gpt-5.5',
    },
    'gemini-3.1-pro-preview': {
        'provider': 'google',
        'provider_model_id': 'gemini-3.1-pro-preview',
    },
    'claude-sonnet-5': {
        'provider': 'anthropic',
        'provider_model_id': 'claude-sonnet-5',
    },
}

MODEL_ALIASES: Dict[str, str] = {
    'gpt-5.5': 'gpt-5.5',
    'gpt-5': 'gpt-5.5',
    'gpt': 'gpt-5.5',
    'gpt-5.2': 'gpt-5.5',
    'gemini-3.1-pro-preview': 'gemini-3.1-pro-preview',
    'gemini-3-pro-preview': 'gemini-3.1-pro-preview',
    'gemini': 'gemini-3.1-pro-preview',
    'claude-sonnet-5': 'claude-sonnet-5',
    'claude': 'claude-sonnet-5',
    'claude-opus-4-5': 'claude-sonnet-5',
}

DEFAULT_RETRY_DELAYS = [2, 5, 10]

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
        self.model_registry = dict(STUDY_MODEL_REGISTRY)
        
        # OpenAI (GPT)
        if self.openai_key:
            openai.api_key = self.openai_key
            self.models['gpt-5.5'] = self._call_openai
            logger.info("OpenAI GPT-5.5 initialized")
        
        # Google Gemini
        if self.google_key:
            self.gemini_client = genai.Client(api_key=self.google_key)
            self.models['gemini-3.1-pro-preview'] = self._call_gemini
            logger.info("Google Gemini initialized")
        
        # Anthropic Claude
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
            self.models['claude-sonnet-5'] = self._call_claude
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
    
    def resolve_model_name(self, model_name: str) -> str:
        """Resolve aliases to the canonical study model name."""
        normalized = str(model_name or '').strip().lower()
        if model_name in self.models:
            return model_name
        if normalized in MODEL_ALIASES:
            return MODEL_ALIASES[normalized]
        raise ValueError(
            f"Model '{model_name}' not available. Available canonical models: {list(self.models.keys())}"
        )

    def get_model_info(self, model_name: str) -> Dict[str, str]:
        """Return canonical provider metadata for a model."""
        canonical_name = self.resolve_model_name(model_name)
        return {
            'canonical_model_name': canonical_name,
            **self.model_registry[canonical_name],
        }

    def _call_openai(self, prompt: str, provider_model_id: str, **kwargs) -> str:
        """Call OpenAI GPT.

        When use_web_search=True, uses the Responses API which supports the
        web_search tool. The Chat Completions API does not support web search
        for this model.
        """
        try:
            client = openai.OpenAI(api_key=self.openai_key)

            if kwargs.get('use_web_search', False):
                # Responses API — required for web search with gpt-5.2
                response = client.responses.create(
                    model=provider_model_id,
                    tools=[{"type": "web_search"}],
                    input=prompt,
                )
                return response.output_text
            else:
                # Standard Chat Completions path (no web search)
                # GPT-5.2 requires max_completion_tokens instead of max_tokens
                response = client.chat.completions.create(
                    model=provider_model_id,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0),
                    max_completion_tokens=kwargs.get('max_completion_tokens', kwargs.get('max_tokens', 16000))
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            return f"Error: {str(e)}"
    
    def _call_gemini(self, prompt: str, provider_model_id: str, **kwargs) -> str:
        """Call Google Gemini.

        When use_web_search=True, Google Search grounding is enabled via
        types.Tool(google_search=types.GoogleSearch()).
        NOTE: response_mime_type='application/json' is incompatible with
        Google Search grounding and is omitted in that mode.
        """
        from google.genai import types as genai_types
        try:
            if kwargs.get('use_web_search', False):
                config = genai_types.GenerateContentConfig(
                    tools=[genai_types.Tool(google_search=genai_types.GoogleSearch())],
                    temperature=kwargs.get('temperature', 0),
                )
            else:
                config = genai_types.GenerateContentConfig(
                    response_mime_type='application/json',
                    temperature=kwargs.get('temperature', 0),
                )

            response = self.gemini_client.models.generate_content(
                model=provider_model_id,
                contents=[prompt],
                config=config,
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return f"Error: {str(e)}"
    
    def _call_claude(self, prompt: str, provider_model_id: str, **kwargs) -> str:
        """Call Anthropic Claude.

        When use_web_search=True, the built-in server-side web_search tool is
        enabled (type 'web_search_20250305'). Anthropic executes searches on
        its own servers, so no client-side tool loop is needed. The response
        may contain interleaved tool_use and text blocks; we collect all text
        blocks and join them to form the final answer.
        """
        try:
            create_kwargs = dict(
                model=provider_model_id,
                max_tokens=kwargs.get('max_tokens', 16000),
                temperature=kwargs.get('temperature', 0),
                messages=[{"role": "user", "content": prompt}],
            )

            if kwargs.get('use_web_search', False):
                create_kwargs['tools'] = [
                    {
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 5,
                    }
                ]

            response = self.anthropic_client.messages.create(**create_kwargs)

            # Collect text from all text blocks (web search adds tool_use blocks
            # alongside the text blocks in the response)
            text_parts = [
                block.text for block in response.content
                if hasattr(block, 'text')
            ]
            return '\n'.join(text_parts)
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
    
    def _call_model_once(self, prompt: str, canonical_model_name: str, **kwargs) -> str:
        call_fn = self.models[canonical_model_name]
        provider_model_id = self.model_registry[canonical_model_name]['provider_model_id']
        return call_fn(prompt, provider_model_id=provider_model_id, **kwargs)

    def generate_content_with_metadata(self, prompt: str, model_name: str = 'gemini-3.1-pro-preview', **kwargs) -> Dict[str, Any]:
        """
        Generate content and return study-friendly metadata for logging.
        """
        canonical_model_name = self.resolve_model_name(model_name)
        if canonical_model_name not in self.models:
            available_models = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not available. Available models: {available_models}")

        retry_delays = list(kwargs.pop('retry_delays', DEFAULT_RETRY_DELAYS))
        attempts = 1 + len(retry_delays)
        last_error = None
        raw_response = None

        for attempt_idx in range(attempts):
            started_at = datetime.now().isoformat()
            try:
                raw_response = self._call_model_once(prompt, canonical_model_name, **kwargs)
                if isinstance(raw_response, str) and raw_response.startswith("Error: "):
                    raise RuntimeError(raw_response[7:])

                return {
                    'requested_model_name': model_name,
                    'canonical_model_name': canonical_model_name,
                    'provider': self.model_registry[canonical_model_name]['provider'],
                    'provider_model_id': self.model_registry[canonical_model_name]['provider_model_id'],
                    'temperature': kwargs.get('temperature', 0),
                    'max_tokens': kwargs.get('max_tokens', kwargs.get('max_completion_tokens', 16000)),
                    'timestamp': started_at,
                    'raw_response': raw_response,
                    'attempt_count': attempt_idx + 1,
                    'retry_delays_seconds': retry_delays,
                    'error': None,
                }
            except Exception as exc:
                last_error = str(exc)
                if attempt_idx < len(retry_delays):
                    delay = retry_delays[attempt_idx]
                    logger.warning(
                        "Retrying %s after error on attempt %s/%s in %ss: %s",
                        canonical_model_name,
                        attempt_idx + 1,
                        attempts,
                        delay,
                        exc,
                    )
                    time.sleep(delay)

        return {
            'requested_model_name': model_name,
            'canonical_model_name': canonical_model_name,
            'provider': self.model_registry[canonical_model_name]['provider'],
            'provider_model_id': self.model_registry[canonical_model_name]['provider_model_id'],
            'temperature': kwargs.get('temperature', 0),
            'max_tokens': kwargs.get('max_tokens', kwargs.get('max_completion_tokens', 16000)),
            'timestamp': datetime.now().isoformat(),
            'raw_response': raw_response or '',
            'attempt_count': attempts,
            'retry_delays_seconds': retry_delays,
            'error': last_error or 'unknown error',
        }

    def generate_content(self, prompt: str, model_name: str = 'gemini-3.1-pro-preview', **kwargs) -> str:
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
        result = self.generate_content_with_metadata(prompt, model_name=model_name, **kwargs)
        if result['error']:
            raise RuntimeError(
                f"Generation failed for {result['canonical_model_name']}: {result['error']}"
            )
        return result['raw_response']
    
    def generate_research_ideas(self, research_call: str, model_name: str, 
                               prompt_template: str = None, **kwargs) -> AIResponse:
        """Generate research ideas based on the research call using a specific model"""
        canonical_model_name = self.resolve_model_name(model_name)
        template_name = prompt_template or self.current_template
        prompt = self.prompt_manager.format_prompt(template_name, {'research_call': research_call})

        result = self.generate_content_with_metadata(prompt, model_name=canonical_model_name, **kwargs)
        raw_response = result['raw_response']
        
        # Try to parse JSON response
        parsed_ideas = self._parse_json_response(raw_response)
        
        # Create response object
        response = AIResponse(
            model_name=canonical_model_name,
            session_id='research_call_session',  # Since we're working with research call
            generated_ideas=parsed_ideas,
            timestamp=datetime.now().isoformat(),
            metadata={
                'temperature': kwargs.get('temperature', 0),
                'max_tokens': kwargs.get('max_tokens', 16000),
                'prompt_template': template_name,
                'research_call': research_call,
                'raw_response': raw_response,
                'parsed_successfully': parsed_ideas is not None,
                'provider_model_id': result['provider_model_id'],
                'attempt_count': result['attempt_count'],
                'error': result['error'],
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
        return sorted(self.models.keys())
    
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
