import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VoiceManager:
    """Manages routing of TTS requests for specific agents."""
    
    def __init__(self, provider_registry) -> None:
        self._registry: Dict[str, Dict[str, Any]] = {}
        self.provider_registry = provider_registry
        
    def register(self, agent_id: str, provider: str, voice_id: str = "default", **kwargs: Any) -> None:
        """Register a voice preference for an agent."""
        self._registry[agent_id.lower()] = {
            "provider": provider,
            "voice_id": voice_id,
            **kwargs
        }
        
    def get_voice_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve voice config for an agent."""
        return self._registry.get(agent_id.lower())
        
    def synthesize_for_agent(self, agent_id: str, text: str) -> bytes:
        """Synthesize speech for a specific agent, automatically falling back if needed."""
        config = self.get_voice_config(agent_id)
        
        # Default fallback is Alfred's provider (pyttsx3)
        fallback_provider = "pyttsx3"
        fallback_voice_id = "default"
        
        if config:
            provider_name = config["provider"]
            voice_id = config["voice_id"]
            reference = config.get("reference")
        else:
            provider_name = fallback_provider
            voice_id = fallback_voice_id
            reference = None
            
        logger.info(f"VoiceManager: Synthesizing for {agent_id} using {provider_name}")
        
        try:
            # Try to get the specific provider instance
            providers = self.provider_registry.get_providers("TTS")
            provider = next((p for p in providers if p.capability.name == provider_name), None)
            if provider:
                # Pass reference if available, otherwise just text and voice_id
                if reference and hasattr(provider, "synthesize_with_reference"):
                    return provider.synthesize_with_reference(text, reference)
                else:
                    return provider.synthesize(text, voice_id)
        except Exception as e:
            logger.error(f"VoiceManager: Provider {provider_name} failed for {agent_id}: {e}")
            
        # Fallback to Alfred's TTS
        if provider_name != fallback_provider:
            logger.info(f"VoiceManager: Falling back to {fallback_provider} for {agent_id}")
            try:
                providers = self.provider_registry.get_providers("TTS")
                fallback = next((p for p in providers if p.capability.name == fallback_provider), None)
                if fallback:
                    return fallback.synthesize(text, fallback_voice_id)
            except Exception as e:
                logger.error(f"VoiceManager: Fallback provider {fallback_provider} also failed: {e}")
                
        return b""
