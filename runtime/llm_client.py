"""LLM Client Interface - Reusable across all projects."""

import json
from typing import Any, Dict, Optional

import requests

class LLMClient:
    """Reusable LLM client supporting multiple providers."""
    
    def __init__(
        self,
        provider: str = "ollama",
        model: str = "mistral",
        region: Optional[str] = None,
        credentials: Optional[Dict[str, str]] = None,
        endpoint: Optional[str] = None,
        timeout_seconds: int = 1800,
    ):
        self.provider = provider
        self.model = model
        self.region = region
        self.credentials = credentials or {}
        self.timeout_seconds = timeout_seconds
        
        if provider == "ollama":
            self.endpoint = endpoint or "http://localhost:11434/api/generate"
        elif provider == "bedrock":
            import boto3
            self.client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                **credentials
            )
        elif provider == "openai":
            self.api_key = credentials.get("api_key")
            self.endpoint = endpoint or "https://api.openai.com/v1/chat/completions"
    
    def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Query LLM with prompt and optional system prompt"""
        
        if self.provider == "ollama":
            return self._query_ollama(prompt, system_prompt, **kwargs)
        elif self.provider == "bedrock":
            return self._query_bedrock(prompt, system_prompt, **kwargs)
        elif self.provider == "openai":
            return self._query_openai(prompt, system_prompt, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _query_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Query Ollama API"""
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": True,
        }
        payload.update(kwargs)
        payload["stream"] = True

        # Use streamed NDJSON so slower local models keep the connection alive.
        with requests.post(
            self.endpoint,
            json=payload,
            timeout=(10, self.timeout_seconds),
            stream=True,
        ) as response:
            response.raise_for_status()
            chunks = []
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                data = json.loads(line)
                chunks.append(data.get("response", ""))
                if data.get("done"):
                    break
            return "".join(chunks).strip()
    
    def _query_bedrock(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Query AWS Bedrock API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "modelId": self.model,
            "messages": messages,
            "maxTokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        response = self.client.invoke_model(**payload)
        return response["output"]["message"]["content"][0]["text"].strip()
    
    def _query_openai(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Query OpenAI API"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.endpoint,
            json=payload,
            headers=headers,
            timeout=(10, self.timeout_seconds),
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
