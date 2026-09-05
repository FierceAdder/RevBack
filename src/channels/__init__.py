"""Channel dispatch package for RevBack multi-channel communication (Email, SMS, WhatsApp)."""

from src.channels.email import EmailDispatcher
from src.channels.sms import SMSDispatcher
from src.channels.whatsapp import WhatsAppDispatcher

__all__ = ["EmailDispatcher", "SMSDispatcher", "WhatsAppDispatcher"]
