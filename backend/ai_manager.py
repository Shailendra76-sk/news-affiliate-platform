import os
import logging
import asyncio
import time
from dotenv import load_dotenv
import httpx

load_dotenv()
logger = logging.getLogger(__name__)

AI_PROVIDERS = [
    {"provider": "groq", "key_env": "GROQ_API_KEY_1", 
     "model": "llama-3.3-70b-versatile", "priority": 1},
    {"provider": "groq", "key_env": "GROQ_API_KEY_2", 
     "model": "llama-3.3-70b-versatile", "priority": 1},
    {"provider": "groq", "key_env": "GROQ_API_KEY_3", 
     "model": "llama-3.3-70b-versatile", "priority": 1},
    {"provider": "deepseek", "key_env": "DEEPSEEK_API_KEY", 
     "model": "deepseek-chat", "priority": 2},
    {"provider": "mistral", "key_env": "MISTRAL_API_KEY", 
     "model": "mistral-small-latest", "priority": 3},
    {"provider": "cohere", "key_env": "COHERE_API_KEY", 
     "model": "command-r", "priority": 4},
    {"provider": "together", "key_env": "TOGETHER_API_KEY", 
     "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo", "priority": 5},
    {"provider": "openrouter", "key_env": "OPENROUTER_API_KEY", 
     "model": "meta-llama/llama-3.1-8b-instruct:free", "priority": 6},
]

failed_providers = {}
COOLDOWN_TIME = 3600


class AIManager:

    def __init__(self):
        self.providers = AI_PROVIDERS

    def _is_available(self, provider_config):
        key = f"{provider_config['provider']}_{provider_config['key_env']}"
        if key in failed_providers:
            if time.time() - failed_providers[key] < COOLDOWN_TIME:
                return False
            else:
                del failed_providers[key]
        api_key = os.getenv(provider_config['key_env'])
        return bool(api_key)

    def _mark_failed(self, provider_config):
        key = f"{provider_config['provider']}_{provider_config['key_env']}"
        failed_providers[key] = time.time()
        logger.warning(f"Provider marked as failed: {provider_config['provider']}")

    async def _call_groq(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_deepseek(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_mistral(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_cohere(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.cohere.com/v2/chat",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"][0]["text"]

    async def _call_together(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def _call_openrouter(self, api_key, model, prompt):
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("APP_URL", "http://localhost"),
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def generate(self, prompt: str, task_type: str = "general") -> dict:
        sorted_providers = sorted(
            self.providers,
            key=lambda x: x['priority']
        )

        for provider_config in sorted_providers:
            if not self._is_available(provider_config):
                continue

            api_key = os.getenv(provider_config['key_env'])
            provider = provider_config['provider']
            model = provider_config['model']

            try:
                logger.info(f"Trying {provider} with model {model}")
                start_time = time.time()

                if provider == "groq":
                    content = await self._call_groq(api_key, model, prompt)
                elif provider == "deepseek":
                    content = await self._call_deepseek(api_key, model, prompt)
                elif provider == "mistral":
                    content = await self._call_mistral(api_key, model, prompt)
                elif provider == "cohere":
                    content = await self._call_cohere(api_key, model, prompt)
                elif provider == "together":
                    content = await self._call_together(api_key, model, prompt)
                elif provider == "openrouter":
                    content = await self._call_openrouter(api_key, model, prompt)
                else:
                    continue

                response_time = time.time() - start_time
                logger.info(f"Success with {provider}! Time: {response_time:.2f}s")

                return {
                    "success": True,
                    "content": content,
                    "provider": provider,
                    "model": model,
                    "response_time": response_time
                }

            except httpx.HTTPStatusError as e:
                if e.response.status_code in [429, 503]:
                    self._mark_failed(provider_config)
                    logger.warning(f"{provider} rate limited, trying next...")
                else:
                    logger.error(f"{provider} HTTP error: {e}")
                continue

            except asyncio.TimeoutError:
                logger.warning(f"{provider} timeout, trying next...")
                continue

            except Exception as e:
                logger.error(f"{provider} error: {e}")
                continue

        return {
            "success": False,
            "content": "",
            "provider": "none",
            "model": "none",
            "error": "All AI providers failed!"
        }


ai_manager = AIManager()
