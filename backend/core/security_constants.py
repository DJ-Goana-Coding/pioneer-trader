"""
Security constants used across the application.
These constants ensure consistent validation of credentials.
"""

# Minimum length for API keys and secrets
# Real API keys from exchanges and services are typically 20-50+ characters
# This minimum catches obviously fake/test values while allowing legitimate short keys
MIN_API_KEY_LENGTH = 16

# Minimum length for SECRET_KEY (used for JWT signing)
# Must be at least 32 characters for security (256 bits)
MIN_SECRET_KEY_LENGTH = 32

# Placeholder patterns that indicate test/example values
PLACEHOLDER_PATTERNS = ["PLACEHOLDER", "YOUR_", "EXAMPLE_", "TEST_KEY"]
