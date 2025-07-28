"""Environment configuration management for Supabase connections."""

import os
from dataclasses import dataclass
from typing import Optional
import dotenv

dotenv.load_dotenv()


@dataclass
class EnvironmentConfig:
    """Configuration object that encapsulates all environment-related settings."""
    
    environment: str
    url: str
    anon_key: str
    is_local: bool
    
    @classmethod
    def from_environment(cls) -> "EnvironmentConfig":
        """Create configuration from environment variables."""
        environment = os.getenv("ENVIRONMENT", "production").lower()
        url = os.getenv("SUPABASE_URL") or ""
        anon_key = os.getenv("SUPABASE_ANON_KEY") or ""
        is_local = environment == "local"
        
        return cls(
            environment=environment,
            url=url,
            anon_key=anon_key,
            is_local=is_local
        )
    
    def validate(self) -> tuple[bool, str]:
        """Validate that required configuration is available."""
        if not self.url or not self.anon_key:
            if self.is_local:
                return False, (
                    "Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.\n"
                    "For local development:\n"
                    "1. Run 'supabase start' to start local Supabase\n"
                    "2. Copy .env.local to .env to use local configuration"
                )
            else:
                return False, (
                    "Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables.\n"
                    "Please set these in your .env file for production use."
                )
        
        env_type = "local development" if self.is_local else "production"
        return True, f"Environment validated for {env_type}"
    
    def get_display_name(self) -> str:
        """Get a human-readable display name for the environment."""
        return "local development" if self.is_local else "production"
    
    def get_console_message(self) -> str:
        """Get the console message to display when this configuration is active."""
        if self.is_local:
            return f"🔧 Using local Supabase environment at {self.url}"
        else:
            return "🌐 Using production Supabase environment"