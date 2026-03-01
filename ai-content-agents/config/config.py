"""
Configuration module for AI Content Agents

Loads environment variables for various integrations.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Amazon SP-API Configuration
AMAZON_SELLER_ID = os.getenv("AMAZON_SELLER_ID")
AMAZON_SP_API_CLIENT_ID = os.getenv("AMAZON_SP_API_CLIENT_ID")
AMAZON_SP_API_CLIENT_SECRET = os.getenv("AMAZON_SP_API_CLIENT_SECRET")
AMAZON_SP_API_REFRESH_TOKEN = os.getenv("AMAZON_SP_API_REFRESH_TOKEN")
AMAZON_SP_API_REGION = os.getenv("AMAZON_SP_API_REGION", "us-east-1")
AMAZON_MARKETPLACE_ID = os.getenv("AMAZON_MARKETPLACE_ID", "ATVPDKIKX0DER")
