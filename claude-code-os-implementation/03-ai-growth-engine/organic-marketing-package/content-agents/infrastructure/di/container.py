"""
Dependency Injection Container

Container for managing dependencies in the video generation system.
"""

import logging
from typing import Dict, Any, Type, Callable, Optional, List, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DIContainer:
    """
    Dependency injection container for managing service instances.

    Supports:
    - Singleton pattern for services
    - Factory functions
    - Lazy initialization
    - Dependency resolution
    """

    def __init__(self):
        """Initialize the DI container."""
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}

    def register(
        self,
        name: str,
        service: Any = None,
        factory: Callable = None,
        singleton: bool = True
    ) -> None:
        """
        Register a service or factory.

        Args:
            name: Service name
            service: Service instance (if providing instance)
            factory: Factory function (if lazy initialization)
            singleton: Whether to maintain single instance
        """
        if service is not None:
            if singleton:
                self._singletons[name] = service
            else:
                self._services[name] = service
            logger.debug(f"Registered service: {name} (singleton={singleton})")

        elif factory is not None:
            self._factories[name] = factory
            logger.debug(f"Registered factory for: {name}")

        else:
            raise ValueError("Must provide either service instance or factory")

    def resolve(self, name: str, type_hint: Type[T] = None) -> T:
        """
        Resolve a service by name.

        Args:
            name: Service name
            type_hint: Optional type hint for IDE support

        Returns:
            Service instance

        Raises:
            KeyError: If service not found
        """
        # Check singletons first
        if name in self._singletons:
            return self._singletons[name]

        # Check regular services
        if name in self._services:
            return self._services[name]

        # Check factories
        if name in self._factories:
            instance = self._factories[name]()
            # Store as singleton by default
            self._singletons[name] = instance
            logger.debug(f"Created instance from factory: {name}")
            return instance

        raise KeyError(f"Service not found: {name}")

    def has(self, name: str) -> bool:
        """
        Check if service is registered.

        Args:
            name: Service name

        Returns:
            True if registered
        """
        return (
            name in self._singletons or
            name in self._services or
            name in self._factories
        )

    def get_all_providers(self) -> List[tuple[str, Any]]:
        """
        Get all registered video providers.

        Returns:
            List of (provider_id, provider) tuples
        """
        providers = []

        for name in list(self._singletons.keys()) + list(self._services.keys()):
            if name.endswith("_provider"):
                try:
                    provider = self.resolve(name)
                    providers.append((name, provider))
                except Exception as e:
                    logger.warning(f"Failed to resolve provider {name}: {e}")

        return providers

    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.info("Cleared all services from container")

    def register_module(self, module: 'DIModule') -> None:
        """
        Register services from a module.

        Args:
            module: DIModule instance
        """
        module.configure(self)
        logger.info(f"Registered module: {module.__class__.__name__}")


class DIModule:
    """Base class for DI modules."""

    def configure(self, container: DIContainer) -> None:
        """
        Configure services in the container.

        Args:
            container: DI container to configure
        """
        raise NotImplementedError