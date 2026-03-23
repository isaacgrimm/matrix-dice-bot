"""
Configuration settings for the Matrix Dice Bot.
"""

# Matrix server connection settings
HOMESERVER_URL = "https://matrix.org"  # Change to your Matrix homeserver
USER_ID = "@yourbot:matrix.org"  # Change to your bot's Matrix user ID
ACCESS_TOKEN = "your_access_token_here"  # Replace with your bot's access token

# Optional: Device name for the bot session
DEVICE_NAME = "Matrix Dice Bot"

# Bot settings
COMMAND_PREFIX = "!"  # The prefix used for bot commands
DEFAULT_ROOM_ID = None  # Optional: Default room to operate in (can be None)

# Dice settings
MAX_DICE_COUNT = 10  # Maximum number of dice that can be rolled at once
MAX_DICE_SIDES = 1000  # Maximum number of sides on a die

# Logging settings
LOG_LEVEL = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "bot.log"  # Log file path

# Response settings
SHOW_DETAILS = True  # Show individual die results in addition to total
EMOJI_RESULTS = True  # Use emoji to represent dice results
