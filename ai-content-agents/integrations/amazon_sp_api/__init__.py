"""
Amazon Selling Partner API (SP-API) Integration

Provides Multi-Channel Fulfillment (MCF) capabilities for order processing,
inventory management, and shipment tracking through Amazon's fulfillment network.
"""
from integrations.amazon_sp_api.auth import SPAPIAuth, get_sp_api_credentials, get_access_token
from integrations.amazon_sp_api.mcf_client import MCFClient, MCFClientError
from integrations.amazon_sp_api.models import (
    Address,
    MCFOrderItem,
    MCFFulfillmentOrder,
    MCFPackage,
    MCFShipment,
    MCFInventoryItem,
    ShippingSpeedCategory,
    FulfillmentOrderStatus,
    PackageStatus
)

__all__ = [
    'SPAPIAuth',
    'get_sp_api_credentials',
    'get_access_token',
    'MCFClient',
    'MCFClientError',
    'Address',
    'MCFOrderItem',
    'MCFFulfillmentOrder',
    'MCFPackage',
    'MCFShipment',
    'MCFInventoryItem',
    'ShippingSpeedCategory',
    'FulfillmentOrderStatus',
    'PackageStatus',
]
