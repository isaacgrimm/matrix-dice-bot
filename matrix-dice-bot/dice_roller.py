"""
Dice roller module for Matrix Dice Bot.
Provides dice parsing, rolling, and formatting functionality.
This module is shared between bot.py and console.py.
"""

import random
import re
from typing import List, Optional, Tuple


class DiceRoller:
    """Universal dice roller for standard and Fudge/Fate dice."""

    FUDGE_FACES = ["+", "+", " ", " ", "-", "-"]

    def parse_dice_notation(self, notation: str) -> Optional[dict]:
        """
        Parse dice notation like 'd20', '2d6', '3d10+5', '4d6-2', '4dF', etc.
        Returns dict with dice info or None if invalid.
        """
        # Check for Fudge/Fate dice (dF, dFudge, dFate) with optional modifier
        fudge_pattern = r"^(\d*)d(fudge|fate|f)([+-]\d+)?$"
        fudge_match = re.match(fudge_pattern, notation.strip(), re.IGNORECASE)

        if fudge_match:
            num_dice = int(fudge_match.group(1)) if fudge_match.group(1) else 4
            modifier = int(fudge_match.group(3)) if fudge_match.group(3) else 0
            if num_dice < 1 or num_dice > 100:
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
            return None

        if num_dice < 1 or num_dice > 100:
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
        Each die has faces: [+, +, blank, blank, -, -]
        Returns tuple of (individual_faces, total).
        """
        faces = [random.choice(self.FUDGE_FACES) for _ in range(num_dice)]
        # Convert faces to values: + = +1, blank = 0, - = -1
        values = [{"+": 1, " ": 0, "-": -1}[face] for face in faces]
        total = sum(values) + modifier
        return (faces, total)

    def format_roll_result(
        self, notation: str, dice_info: dict, rolls: List, total: int
    ) -> str:
        """Format the roll result for display."""
        if dice_info["type"] == "fudge":
            # Format Fudge dice: [+ -  ] = 0
            faces_str = "".join(rolls)
            modifier_str = (
                f"{dice_info['modifier']:+d}" if dice_info["modifier"] != 0 else ""
            )
            if dice_info["modifier"] != 0:
                result = f"🔮 {notation} = [{faces_str}]{modifier_str} = {total}"
            else:
                result = f"🔮 {notation} = [{faces_str}] = {total}"
        else:
            # Format standard dice: [4, 5]+3 = 12
            rolls_str = ", ".join(str(r) for r in rolls)
            modifier_str = (
                f"{dice_info['modifier']:+d}" if dice_info["modifier"] != 0 else ""
            )
            if dice_info["modifier"] != 0:
                result = f"🎲 {notation} = [{rolls_str}]{modifier_str} = {total}"
            else:
                result = f"🎲 {notation} = [{rolls_str}] = {total}"
        return result

    def process_roll(self, notation: str) -> Optional[str]:
        """
        Process a dice roll command and return formatted result.
        Returns None if notation is invalid.
        """
        # Parse dice notation
        dice_info = self.parse_dice_notation(notation)
        if dice_info is None:
            return None

        # Roll dice
        if dice_info["type"] == "fudge":
            rolls, total = self.roll_fudge_dice(
                dice_info["num_dice"], dice_info["modifier"]
            )
        else:
            rolls, total = self.roll_dice(
                dice_info["num_dice"], dice_info["sides"], dice_info["modifier"]
            )

        # Format and return result
        return self.format_roll_result(notation, dice_info, rolls, total)
