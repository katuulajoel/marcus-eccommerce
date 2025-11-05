"""
Channel Adapter Base Class
Formats agent responses for different channels (web, WhatsApp, SMS, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import re


class ChannelAdapter(ABC):
    """
    Base class for channel-specific adapters.
    Each channel (web, WhatsApp, SMS) has different formatting requirements.
    """

    @abstractmethod
    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format agent response for this channel.

        Args:
            response: Dict with 'content' and 'metadata' from agent

        Returns:
            Formatted response dict for the channel
        """
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """Get the name of this channel."""
        pass

    def strip_markdown(self, text: str) -> str:
        """
        Strip markdown formatting for channels that don't support it.

        Args:
            text: Text with markdown

        Returns:
            Plain text
        """
        # Remove markdown headers
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

        # Remove bold/italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Italic
        text = re.sub(r'__([^_]+)__', r'\1', text)  # Bold
        text = re.sub(r'_([^_]+)_', r'\1', text)  # Italic

        # Remove links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Remove code blocks
        text = re.sub(r'```[^`]+```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)

        return text

    def truncate_text(self, text: str, max_length: int) -> str:
        """
        Truncate text to max length.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        return text[:max_length - 3] + '...'


class WebChannelAdapter(ChannelAdapter):
    """
    Adapter for web channel (supports markdown, longer messages).
    """

    def get_channel_name(self) -> str:
        return "web"

    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for web channel (minimal changes, supports markdown).
        """
        # Web supports full markdown and longer messages
        return {
            'content': response.get('content', ''),
            'metadata': response.get('metadata', {}),
            'channel': 'web',
        }


class WhatsAppChannelAdapter(ChannelAdapter):
    """
    Adapter for WhatsApp channel.
    WhatsApp supports emojis and limited markdown but has message length limits.
    """

    MAX_MESSAGE_LENGTH = 4096  # WhatsApp message limit

    def get_channel_name(self) -> str:
        return "whatsapp"

    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for WhatsApp channel.
        """
        content = response.get('content', '')

        # WhatsApp supports basic markdown (*bold*, _italic_, ~strikethrough~)
        # But has different syntax than standard markdown

        # Convert **bold** to *bold* (WhatsApp format)
        content = re.sub(r'\*\*([^*]+)\*\*', r'*\1*', content)

        # Convert __italic__ to _italic_
        content = re.sub(r'__([^_]+)__', r'_\1_', content)

        # Remove unsupported markdown (code blocks, headers)
        content = re.sub(r'```[^`]+```', '[code snippet removed]', content, flags=re.DOTALL)
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

        # Truncate if too long
        if len(content) > self.MAX_MESSAGE_LENGTH:
            content = self.truncate_text(content, self.MAX_MESSAGE_LENGTH)

        return {
            'content': content,
            'metadata': response.get('metadata', {}),
            'channel': 'whatsapp',
        }


class SMSChannelAdapter(ChannelAdapter):
    """
    Adapter for SMS channel (very limited: plain text, short messages).
    """

    MAX_MESSAGE_LENGTH = 160  # Standard SMS length

    def get_channel_name(self) -> str:
        return "sms"

    def format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format for SMS channel (very limited).
        """
        content = response.get('content', '')

        # Strip all markdown
        content = self.strip_markdown(content)

        # Remove emojis for SMS
        content = re.sub(r'[^\x00-\x7F]+', '', content)

        # Truncate to SMS length
        if len(content) > self.MAX_MESSAGE_LENGTH:
            content = self.truncate_text(content, self.MAX_MESSAGE_LENGTH)

        return {
            'content': content,
            'metadata': response.get('metadata', {}),
            'channel': 'sms',
        }


# Factory function
def get_channel_adapter(channel: str) -> ChannelAdapter:
    """
    Get adapter for specified channel.

    Args:
        channel: Channel name ('web', 'whatsapp', 'sms')

    Returns:
        ChannelAdapter instance

    Raises:
        ValueError: If channel not supported
    """
    adapters = {
        'web': WebChannelAdapter,
        'whatsapp': WhatsAppChannelAdapter,
        'sms': SMSChannelAdapter,
    }

    adapter_class = adapters.get(channel.lower())
    if not adapter_class:
        raise ValueError(f"Unsupported channel: {channel}. Supported: {list(adapters.keys())}")

    return adapter_class()
