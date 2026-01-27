import json
import os
from typing import Optional
from app.models.schemas import AssistantConfig

class JsonConfigService:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not os.path.exists(self.config_path):
            default_config = AssistantConfig(
                name="Cindy",
                behavior_settings="You are a helpful and friendly voice chat assistant. Keep your responses concise and conversational, suitable for speech output."
            )
            self.save_config(default_config)

    def get_config(self) -> AssistantConfig:
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
            return AssistantConfig(**data)
        except (FileNotFoundError, json.JSONDecodeError):
            # Fallback if file corrupted or missing
            return AssistantConfig(
                name="Cindy",
                behavior_settings="You are a helpful and friendly voice chat assistant."
            )

    def save_config(self, config: AssistantConfig):
        with open(self.config_path, "w") as f:
            json.dump(config.dict(), f, indent=4)
