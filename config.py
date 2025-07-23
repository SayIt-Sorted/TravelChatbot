"""
Configuration management for Travel Chatbot MVP
"""

import os
from typing import Optional
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration manager for the chatbot"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file: {e}")
                return self._get_default_config()
        else:
            # Create default config file
            default_config = self._get_default_config()
            self._save_config(default_config)
            return default_config
    
    def _get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            "openai": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.1
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587
            },
            "flight_search": {
                "use_mock": True,
                "max_results": 5
            },
            "chatbot": {
                "session_timeout_hours": 24,
                "max_conversation_history": 50,
                "default_currency": "EUR"
            },
            "logging": {
                "level": "INFO",
                "log_to_file": False,
                "log_file": "chatbot.log"
            }
        }
    
    def _save_config(self, config: dict):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation (e.g., 'openai.api_key')"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        self._save_config(self.config)
    
    def get_openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or config"""
        # Priority: .env > config.json
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            api_key = self.get('openai.api_key')
        return api_key
    
    def get_email_config(self) -> dict:
        """Get email configuration"""
        return {
            'smtp_server': self.get('email.smtp_server', 'smtp.gmail.com'),
            'smtp_port': self.get('email.smtp_port', 587),
            'email': os.getenv('SMTP_EMAIL') or self.get('email.email'),
            'password': os.getenv('SMTP_PASSWORD') or self.get('email.password')
        }
    
    def get_flight_search_config(self) -> dict:
        """Get flight search configuration"""
        return {
            'use_mock': self.get('flight_search.use_mock', True),
            'amadeus_api_key': os.getenv('AMADEUS_API_KEY') or self.get('flight_search.amadeus_api_key'),
            'amadeus_api_secret': os.getenv('AMADEUS_API_SECRET') or self.get('flight_search.amadeus_api_secret'),
            'max_results': self.get('flight_search.max_results', 5)
        }
    
    def is_configured(self) -> dict:
        """Check which services are properly configured"""
        return {
            'openai': bool(self.get_openai_api_key()),
            'email': bool(self.get_email_config()['email'] and self.get_email_config()['password']),
            'flight_search': bool(self.get_flight_search_config()['amadeus_api_key'] and self.get_flight_search_config()['amadeus_api_secret'])
        }
    
    def print_status(self):
        """Print configuration status"""
        status = self.is_configured()
        
        print("\n🔧 Configuration Status:")
        print("=" * 40)
        
        if status['openai']:
            print("✅ OpenAI API: Configured")
        else:
            print("❌ OpenAI API: Not configured (required)")
            print("   Set OPENAI_API_KEY in .env file")
        
        if status['email']:
            print("✅ Email Service: Configured")
            email_config = self.get_email_config()
            print(f"   Email: {email_config['email']}")
        else:
            print("⚠️  Email Service: Not configured (required for flight summaries)")
            print("   Set SMTP_EMAIL and SMTP_PASSWORD in .env file")
        
        if status['flight_search']:
            print("✅ Flight Search: Real API configured")
        else:
            print("ℹ️  Flight Search: Using mock data")
            print("   Set AMADEUS_API_KEY and AMADEUS_API_SECRET in .env file")
            print("   Get your keys from: https://developers.amadeus.com/")
        
        print("=" * 40)
    
    def setup_interactive(self):
        """Interactive configuration setup"""
        print("\n🔧 Interactive Configuration Setup")
        print("=" * 40)
        print("💡 Secrets (API keys, passwords) should go in .env file")
        print("💡 Settings (timeouts, limits) go in config.json")
        print()
        
        # Check if .env exists
        env_file = Path('.env')
        if not env_file.exists():
            print("📝 Creating .env file for secrets...")
            self._create_env_file()
        
        # OpenAI API Key
        current_key = self.get_openai_api_key()
        if current_key:
            print(f"Current OpenAI API Key: {current_key[:8]}...")
            if input("Change OpenAI API Key? (y/N): ").lower() == 'y':
                new_key = input("Enter OpenAI API Key: ").strip()
                if new_key:
                    self._set_env_var('OPENAI_API_KEY', new_key)
        else:
            new_key = input("Enter OpenAI API Key (required): ").strip()
            if new_key:
                self._set_env_var('OPENAI_API_KEY', new_key)
            else:
                print("❌ OpenAI API Key is required!")
                return False
        
        # Email Configuration
        email_config = self.get_email_config()
        if email_config['email'] and email_config['password']:
            print(f"\nCurrent Email: {email_config['email']}")
            if input("Change email configuration? (y/N): ").lower() == 'y':
                self._setup_email_env()
        else:
            print("\n📧 Email Configuration (Required for flight summaries)")
            if input("Set up email configuration? (y/N): ").lower() == 'y':
                self._setup_email_env()
        
        # Flight Search API
        flight_config = self.get_flight_search_config()
        if flight_config['amadeus_api_key'] and flight_config['amadeus_api_secret']:
            print("\nFlight Search API: Amadeus API configured")
            if input("Change flight search API credentials? (y/N): ").lower() == 'y':
                self._setup_amadeus_env()
        else:
            print("\nFlight Search API: Not configured (using mock data)")
            print("Get your free Amadeus API keys from: https://developers.amadeus.com/")
            if input("Set up Amadeus API credentials? (y/N): ").lower() == 'y':
                self._setup_amadeus_env()
        
        print("\n✅ Configuration updated!")
        self.print_status()
        return True
    
    def _create_env_file(self):
        """Create .env file with template"""
        env_content = """# Travel Chatbot Secrets
# Add your API keys and passwords here
# DO NOT commit this file to version control

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Email Configuration
SMTP_EMAIL=your_email@example.com
SMTP_PASSWORD=your_email_password_here

# Amadeus API (optional - for real flight data)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
    
    def _set_env_var(self, key: str, value: str):
        """Set environment variable in .env file"""
        env_file = Path('.env')
        
        if not env_file.exists():
            self._create_env_file()
        
        # Read current .env content
        lines = []
        if env_file.exists():
            with open(env_file, 'r') as f:
                lines = f.readlines()
        
        # Update or add the variable
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}\n'
                found = True
                break
        
        if not found:
            lines.append(f'{key}={value}\n')
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.writelines(lines)
        
        print(f"✅ Updated {key} in .env file")
    
    def _setup_email_env(self):
        """Setup email environment variables"""
        email = input("Enter email address: ").strip()
        if email:
            self._set_env_var('SMTP_EMAIL', email)
        
        password = input("Enter email password/app password: ").strip()
        if password:
            self._set_env_var('SMTP_PASSWORD', password)
    
    def _setup_amadeus_env(self):
        """Setup Amadeus environment variables"""
        api_key = input("Enter Amadeus API Key: ").strip()
        if api_key:
            self._set_env_var('AMADEUS_API_KEY', api_key)
        
        api_secret = input("Enter Amadeus API Secret: ").strip()
        if api_secret:
            self._set_env_var('AMADEUS_API_SECRET', api_secret)


# Global config instance
config = Config() 