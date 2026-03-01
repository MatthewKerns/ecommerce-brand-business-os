"""
Secrets encryption and management for AI Content Agents
"""
import os
import base64
from pathlib import Path
from typing import Optional

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
except ImportError:
    raise ImportError(
        "cryptography library is required. Install with: pip install cryptography"
    )


class SecretsManager:
    """
    Manages encryption and decryption of sensitive configuration values.

    Uses Fernet symmetric encryption with keys derived from environment variables.
    Supports both direct encryption keys and password-based key derivation.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the secrets manager.

        Args:
            encryption_key: Base64-encoded encryption key. If not provided,
                          will attempt to load from ENCRYPTION_KEY environment variable.
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY", "")

        if not encryption_key:
            # Generate a temporary key for development
            # In production, this should always be provided via environment variable
            encryption_key = Fernet.generate_key().decode()

        self._fernet = self._initialize_fernet(encryption_key)

    def _initialize_fernet(self, key: str) -> Fernet:
        """
        Initialize Fernet cipher with the provided key.

        Args:
            key: Encryption key (base64-encoded or password)

        Returns:
            Fernet cipher instance
        """
        try:
            # Try to use the key directly (assumes it's base64-encoded)
            return Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # If direct usage fails, derive a key from the password
            return Fernet(self._derive_key(key))

    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive an encryption key from a password using PBKDF2.

        Args:
            password: Password to derive key from
            salt: Salt for key derivation (default: fixed salt for consistency)

        Returns:
            Base64-encoded encryption key
        """
        if salt is None:
            # Use a fixed salt for consistency across sessions
            # In production, consider storing salt securely
            salt = b"ai-content-agents-salt"

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: The string to encrypt

        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""

        encrypted_bytes = self._fernet.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            ciphertext: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string
        """
        if not ciphertext:
            return ""

        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {str(e)}")

    def encrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Encrypt a file's contents.

        Args:
            input_path: Path to plaintext file
            output_path: Path to write encrypted file
        """
        with open(input_path, 'r') as f:
            plaintext = f.read()

        encrypted = self.encrypt(plaintext)

        with open(output_path, 'w') as f:
            f.write(encrypted)

    def decrypt_file(self, input_path: Path, output_path: Path) -> None:
        """
        Decrypt a file's contents.

        Args:
            input_path: Path to encrypted file
            output_path: Path to write decrypted file
        """
        with open(input_path, 'r') as f:
            ciphertext = f.read()

        decrypted = self.decrypt(ciphertext)

        with open(output_path, 'w') as f:
            f.write(decrypted)

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.

        Returns:
            Base64-encoded encryption key
        """
        return Fernet.generate_key().decode()


# Default instance for convenience
_default_manager: Optional[SecretsManager] = None


def get_secrets_manager() -> SecretsManager:
    """
    Get the default SecretsManager instance.

    Returns:
        SecretsManager instance
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = SecretsManager()
    return _default_manager


def encrypt_secret(plaintext: str) -> str:
    """
    Convenience function to encrypt a secret using the default manager.

    Args:
        plaintext: The string to encrypt

    Returns:
        Base64-encoded encrypted string
    """
    return get_secrets_manager().encrypt(plaintext)


def decrypt_secret(ciphertext: str) -> str:
    """
    Convenience function to decrypt a secret using the default manager.

    Args:
        ciphertext: Base64-encoded encrypted string

    Returns:
        Decrypted plaintext string
    """
    return get_secrets_manager().decrypt(ciphertext)
