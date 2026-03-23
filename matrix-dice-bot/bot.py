#!/usr/bin/env python3
"""
Matrix Dice Bot - Бот для сети Matrix с поддержкой бросания кубов.
Supports dice notation like d20, d6, d100, and Russian commands.
Automatically accepts room invites and works in DMs.
"""

import asyncio
import logging
import random
import re
import sys
from typing import List, Optional, Tuple

from nio import AsyncClient, InviteEvent, MatrixRoom, RoomMessageNotice, RoomMessageText

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


class DiceBot:
    """Matrix bot for rolling dice in chat."""

    # Supported dice types
    SUPPORTED_DICE = [4, 6, 8, 10, 12, 20, 100]

    # Fudge/Fate dice faces: [+，+, blank, blank, -, -]
    FUDGE_FACES = ["+", "+", " ", " ", "-", "-"]

    # Russian command aliases
    ROLL_COMMANDS = ["roll", "dice", "кинь", "брось", "куб", "кубы", "кости"]
    HELP_COMMANDS = ["help", "помощь", "справка", "h", "?"]

    def __init__(
        self,
        homeserver_url: str,
        username: str,
        password: Optional[str] = None,
        access_token: Optional[str] = None,
        device_name: str = "Matrix Dice Bot",
    ):
        self.homeserver_url = homeserver_url
        self.username = username
        self.password = password
        self.access_token = access_token
        self.device_name = device_name
        self.client: Optional[AsyncClient] = None
        self.room_ids: List[str] = []
        self.auto_accept_invites = True

    async def connect(self) -> None:
        """Connect to Matrix server."""
        self.client = AsyncClient(
            self.homeserver_url, self.username, device_name=self.device_name
        )

        if self.access_token:
            self.client.access_token = self.access_token
            logger.info("Using access token for authentication")
        elif self.password:
            response = await self.client.login(self.password)
            if isinstance(response, Exception):
                logger.error(f"Login failed: {response}")
                raise response
            logger.info(f"Logged in as {self.username}")
        else:
            raise ValueError("Either password or access_token must be provided")

    async def join_room(self, room_id_or_alias: str) -> None:
        """Join a Matrix room."""
        response = await self.client.join(room_id_or_alias)
        if isinstance(response, Exception):
            logger.error(f"Failed to join room: {response}")
            raise response
        room_id = response.room_id if hasattr(response, "room_id") else room_id_or_alias
        if room_id not in self.room_ids:
            self.room_ids.append(room_id)
        logger.info(f"Joined room: {room_id}")

    async def send_message(
        self,
        room_id: str,
        message: str,
        message_type: str = "m.text",
        formatted_body: Optional[str] = None,
    ) -> None:
        """Send a message to a Matrix room."""
        content = {
            "msgtype": message_type,
            "body": message,
        }

        if formatted_body:
            content["format"] = "org.matrix.custom.html"
            content["formatted_body"] = formatted_body

        response = await self.client.room_put(room_id, "", content)

        if isinstance(response, Exception):
            logger.error(f"Failed to send message: {response}")
            raise response

    def parse_dice_notation(self, notation: str) -> Optional[dict]:
        """
        Parse dice notation like 'd20', '2d6', '3d10+5', '4d6-2', '4dF', etc.
        Returns dict with dice info or None if invalid.
        """
        import re

        # Check for Fudge/Fate dice (dF, dFudge, dFate) with optional modifier
        fudge_pattern = r"^(\d*)d(fudge|fate|f)([+-]\d+)?$"
        fudge_match = re.match(fudge_pattern, notation.strip(), re.IGNORECASE)

        if fudge_match:
            num_dice = int(fudge_match.group(1)) if fudge_match.group(1) else 4
            modifier = int(fudge_match.group(3)) if fudge_match.group(3) else 0
            if num_dice < 1 or num_dice > 100:
                logger.warning(f"Invalid Fudge dice count: {num_dice}")
                return None
            return {"type": "fudge", "num_dice": num_dice, "modifier": modifier}

        # Standard dice notation: NdS[+/-M]
        pattern = r"^(\d*)d(\d+)([+-]\d+)?$"
        match = re.match(pattern, notation.strip(), re.IGNORECASE)

        if not match:
            return None

        num_dice = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        # Validate dice
        if sides < 1 or sides > 1000:
            logger.warning(f"Invalid dice sides: {sides}")
            return None

        if num_dice < 1 or num_dice > 100:
            logger.warning(f"Invalid dice count: {num_dice}")
            return None

        return {
            "type": "standard",
            "num_dice": num_dice,
            "sides": sides,
            "modifier": modifier,
        }

    def roll_dice(
        self, num_dice: int, sides: int, modifier: int = 0
    ) -> Tuple[List[int], int]:
        """
        Roll standard dice and return results.
        Returns tuple of (individual_rolls, total).
        """
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier
        return (rolls, total)

    def roll_fudge_dice(
        self, num_dice: int, modifier: int = 0
    ) -> Tuple[List[str], int]:
        """
        Roll Fudge/Fate dice and return results.
        Each die has faces: [+，+, blank, blank, -, -]
        Returns tuple of (individual_faces, total).
        """
        faces = [random.choice(self.FUDGE_FACES) for _ in range(num_dice)]
        # Convert faces to values: + = +1, blank = 0, - = -1
        values = [{"+": 1, " ": 0, "-": -1}[face] for face in faces]
        total = sum(values) + modifier
        return (faces, total)

    def format_roll_result(
        self,
        notation: str,
        rolls: List,
        total: int,
        modifier: int = 0,
        dice_type: str = "standard",
    ) -> str:
        """Format the dice roll result for display."""
        if dice_type == "fudge":
            # Fudge dice display: show faces and total
            faces_str = "".join(rolls)
            result = f"🔮 {notation} = [{faces_str}] = {total}"
            if modifier != 0:
                sign = "+" if modifier > 0 else ""
                result = f"🔮 {notation} = [{faces_str}]{sign}{modifier} = {total}"
        elif len(rolls) == 1:
            if modifier != 0:
                sign = "+" if modifier > 0 else ""
                result = f"🎲 {notation} = {rolls[0]}{sign}{modifier} = {total}"
            else:
                result = f"🎲 {notation} = {rolls[0]}"
        else:
            rolls_str = " + ".join(map(str, rolls))
            if modifier != 0:
                sign = "+" if modifier > 0 else ""
                result = f"🎲 {notation} = [{rolls_str}]{sign}{modifier} = {total}"
            else:
                result = f"🎲 {notation} = [{rolls_str}] = {total}"

        return result

    def format_help_message(self) -> str:
        """Format help message for users."""
        help_text = """
🎲 <b>Matrix Dice Bot - Справка</b>

<b>Доступные команды:</b>
• !roll &lt;кубы&gt; - бросить кубы
• !d&lt;стороны&gt; - быстро бросить куб
• !help - показать эту справку

<b>Примеры:</b>
• !roll d20 - один куб d20
• !roll 2d6 - два куба d6
• !roll 3d8+2 - три куба d8 + 2
• !roll 4d10-1 - четыре куба d10 - 1
• !roll 4dF - четыре куба Fudge/Fate
• !d6 - быстро бросить d6

<b>Поддерживаемые кубы:</b>
d4, d6, d8, d10, d12, d20, d100, dF (Fudge/Fate)

<b>Кубы Fudge/Fate:</b>
6 граней: [+，+, пустая, пустая, -, -]
Результат: от -4 до +4 для 4dF

<b>Русские команды:</b>
!кинь d20, !брось 2d6, !кубы 3d8
""".strip()
        return help_text

    async def handle_message(self, room: MatrixRoom, event: RoomMessageText) -> None:
        """Handle incoming messages and process dice commands."""
        # Ignore bot's own messages
        if event.sender == self.client.user_id:
            return

        # Only process messages from rooms the bot has joined
        if event.room_id not in self.room_ids:
            return

        body = event.body.strip()

        # Check for command prefix
        prefixes = ["!", "/", "."]
        command_prefix = None

        for prefix in prefixes:
            if body.startswith(prefix):
                command_prefix = prefix
                command = body[len(prefix) :].strip().lower()
                break

        if not command_prefix:
            return

        # Check for help command
        for help_cmd in self.HELP_COMMANDS:
            if command == help_cmd or command.startswith(help_cmd + " "):
                await self.send_message(
                    room.room_id,
                    self.format_help_message(),
                    formatted_body=self.format_help_message(),
                )
                return

        # Check for roll/dice commands
        for roll_cmd in self.ROLL_COMMANDS:
            if command.startswith(roll_cmd):
                # Extract dice notation from command
                remaining = command[len(roll_cmd) :].strip()

                # Look for dice notation in the remaining text
                dice_match = re.search(r"(\d*d\d+[+-]?\d*)", remaining, re.IGNORECASE)

                if dice_match:
                    dice_notation = dice_match.group(1)
                    await self.process_dice_roll(room.room_id, dice_notation)
                    return
                else:
                    # No dice notation found, send error
                    await self.send_message(
                        room.room_id,
                        "❌ Укажите кубы для броска. Пример: !roll d20 или !кинь 2d6",
                    )
                    return

        # Check for simple dice notation without command word (e.g., !d20)
        if re.match(r"\d*d\d+", command, re.IGNORECASE):
            await self.process_dice_roll(room.room_id, command)
            return

    async def process_dice_roll(self, room_id: str, dice_notation: str) -> None:
        """Process a dice roll command and send result."""
        try:
            parsed = self.parse_dice_notation(dice_notation)

            if not parsed:
                await self.send_message(
                    room_id,
                    f"❌ Неправильный формат: {dice_notation}. Используйте формат NdS (например, 2d6, d20) или NdF для Fudge (4dF)",
                )
                return

            if parsed.get("type") == "fudge":
                num_dice = parsed["num_dice"]
                modifier = parsed.get("modifier", 0)
                rolls, total = self.roll_fudge_dice(num_dice, modifier)
                result = self.format_roll_result(
                    dice_notation, rolls, total, modifier, dice_type="fudge"
                )
            else:
                num_dice = parsed["num_dice"]
                sides = parsed["sides"]
                modifier = parsed.get("modifier", 0)
                rolls, total = self.roll_dice(num_dice, sides, modifier)
                result = self.format_roll_result(
                    dice_notation, rolls, total, modifier, dice_type="standard"
                )

            await self.send_message(room_id, result)
            logger.info(f"Processed dice roll: {dice_notation} = {total} in {room_id}")

        except Exception as e:
            logger.error(f"Error processing dice roll: {e}")
            await self.send_message(room_id, f"❌ Ошибка при броске кубов: {str(e)}")

    async def handle_invite(self, room: MatrixRoom, event: InviteEvent) -> None:
        """Handle room invites and auto-accept them."""
        if not self.auto_accept_invites:
            logger.info(
                f"Received invite to {room.room_id}, but auto-accept is disabled"
            )
            return

        try:
            logger.info(f"Received invite to room: {room.room_id}, accepting...")
            response = await self.client.join(room.room_id)
            if isinstance(response, Exception):
                logger.error(f"Failed to accept invite: {response}")
                return

            room_id = response.room_id if hasattr(response, "room_id") else room.room_id
            if room_id not in self.room_ids:
                self.room_ids.append(room_id)

            inviter = event.sender
            logger.info(f"Successfully joined {room_id}, invited by {inviter}")

            # Send welcome message to the new room
            welcome_msg = """🎲 <b>Matrix Dice Bot подключился к комнате!</b>

<b>Доступные команды:</b>
• !roll &lt;кубы&gt; - бросить кубы (например, !roll d20, !roll 2d6)
• !d&lt;стороны&gt; - быстро бросить куб (например, !d6)
• !кинь &lt;кубы&gt; - русская команда
• !help - показать справку

<b>Примеры:</b>
• !roll d20 - один куб d20
• !roll 2d6 - два куба d6
• !roll 3d8+2 - три куба d8 + 2
• !roll 4dF - четыре куба Fudge/Fate

Приятной игры! 🎲"""
            await self.send_message(room_id, welcome_msg, formatted_body=welcome_msg)

        except Exception as e:
            logger.error(f"Error handling invite: {e}")

    async def run(self, room_ids: Optional[List[str]] = None) -> None:
        """Main bot loop."""
        await self.connect()

        # Join specified rooms if provided (optional)
        if room_ids:
            for room_id in room_ids:
                await self.join_room(room_id)
            logger.info(f"Bot joined {len(room_ids)} room(s): {', '.join(room_ids)}")
        else:
            logger.info(
                "Bot started without pre-configured rooms, waiting for invites..."
            )

        # Add event handlers
        self.client.add_event_callback(self.handle_message, RoomMessageText)
        self.client.add_event_callback(self.handle_message, RoomMessageNotice)
        self.client.add_event_callback(self.handle_invite, InviteEvent)

        logger.info("Supported commands: !roll d20, !d6, !3d8+2, !кинь 2d6, !help")
        logger.info("Bot will auto-accept room invites and work in DMs")

        # Start syncing
        try:
            await self.client.sync_forever(timeout=30000)
        except Exception as e:
            logger.error(f"Sync error: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Matrix server."""
        if self.client:
            await self.client.close()
            logger.info("Bot disconnected")


async def main():
    """Entry point for the bot."""
    import os

    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    homeserver = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
    username = os.getenv("MATRIX_USERNAME")
    password = os.getenv("MATRIX_PASSWORD")
    access_token = os.getenv("MATRIX_ACCESS_TOKEN")
    rooms_str = os.getenv("MATRIX_ROOMS", os.getenv("MATRIX_ROOM", ""))
    rooms = (
        [r.strip() for r in rooms_str.split(",") if r.strip()] if rooms_str else None
    )

    if not username:
        logger.error("MATRIX_USERNAME must be set in environment")
        return

    if not password and not access_token:
        logger.error("Either MATRIX_PASSWORD or MATRIX_ACCESS_TOKEN must be set")
        return

    bot = DiceBot(
        homeserver_url=homeserver,
        username=username,
        password=password,
        access_token=access_token,
    )

    try:
        await bot.run(rooms if rooms else [])
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
