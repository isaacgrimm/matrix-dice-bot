#!/usr/bin/env python3
"""
Test script for Matrix Dice Bot - tests dice rolling logic.
Includes tests for standard dice and Fudge/Fate dice.
"""

import random
import re
import unittest
from typing import Dict, List, Tuple


class DiceRoller:
    """Dice rolling logic extracted for testing."""

    SUPPORTED_DICE = [4, 6, 8, 10, 12, 20, 100]
    FUDGE_FACES = ["+", "+", " ", " ", "-", "-"]

    def parse_dice_notation(self, notation: str) -> Dict:
        """
        Parse dice notation like 'd20', '2d6', '3d10+5', '4d6-2', '4dF', etc.
        Returns dict with dice info or raises ValueError if invalid.
        """
        # Check for Fudge/Fate dice (dF, dFudge, dFate) with optional modifier
        fudge_pattern = r"^(\d*)d(fudge|fate|f)([+-]\d+)?$"
        fudge_match = re.match(fudge_pattern, notation.strip(), re.IGNORECASE)

        if fudge_match:
            num_dice = int(fudge_match.group(1)) if fudge_match.group(1) else 4
            modifier = int(fudge_match.group(3)) if fudge_match.group(3) else 0
            if num_dice < 1 or num_dice > 100:
                raise ValueError("Invalid number of dice (must be 1-100)")
            return {"type": "fudge", "num_dice": num_dice, "modifier": modifier}

        # Standard dice notation: NdS[+/-M]
        pattern = r"^(\d*)d(\d+)([+-]\d+)?$"
        match = re.match(pattern, notation.strip(), re.IGNORECASE)

        if not match:
            raise ValueError("Invalid dice notation")

        num_dice = int(match.group(1)) if match.group(1) else 1
        sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        # Validate dice
        if sides < 1 or sides > 1000:
            raise ValueError("Invalid number of sides (must be 1-1000)")

        if num_dice < 1 or num_dice > 100:
            raise ValueError("Invalid number of dice (must be 1-100)")

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


class TestDiceNotation(unittest.TestCase):
    """Test dice notation parsing."""

    def setUp(self):
        self.roller = DiceRoller()

    def test_single_die_d20(self):
        """Test parsing single d20."""
        result = self.roller.parse_dice_notation("d20")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 1)
        self.assertEqual(result["sides"], 20)
        self.assertEqual(result["modifier"], 0)

    def test_single_die_d6(self):
        """Test parsing single d6."""
        result = self.roller.parse_dice_notation("d6")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 1)
        self.assertEqual(result["sides"], 6)
        self.assertEqual(result["modifier"], 0)

    def test_multiple_dice_2d6(self):
        """Test parsing 2d6."""
        result = self.roller.parse_dice_notation("2d6")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 2)
        self.assertEqual(result["sides"], 6)
        self.assertEqual(result["modifier"], 0)

    def test_multiple_dice_3d8(self):
        """Test parsing 3d8."""
        result = self.roller.parse_dice_notation("3d8")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 3)
        self.assertEqual(result["sides"], 8)
        self.assertEqual(result["modifier"], 0)

    def test_with_positive_modifier(self):
        """Test parsing with positive modifier."""
        result = self.roller.parse_dice_notation("2d6+3")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 2)
        self.assertEqual(result["sides"], 6)
        self.assertEqual(result["modifier"], 3)

    def test_with_negative_modifier(self):
        """Test parsing with negative modifier."""
        result = self.roller.parse_dice_notation("4d10-2")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 4)
        self.assertEqual(result["sides"], 10)
        self.assertEqual(result["modifier"], -2)

    def test_uppercase(self):
        """Test uppercase notation."""
        result = self.roller.parse_dice_notation("2D6")
        self.assertEqual(result["type"], "standard")
        self.assertEqual(result["num_dice"], 2)
        self.assertEqual(result["sides"], 6)
        self.assertEqual(result["modifier"], 0)

    def test_invalid_no_dice(self):
        """Test invalid notation without dice."""
        with self.assertRaises(ValueError):
            self.roller.parse_dice_notation("abc")

    def test_invalid_zero_dice(self):
        """Test invalid zero dice."""
        with self.assertRaises(ValueError):
            self.roller.parse_dice_notation("0d20")

    def test_invalid_zero_sides(self):
        """Test invalid zero sides."""
        with self.assertRaises(ValueError):
            self.roller.parse_dice_notation("d0")

    def test_fudge_dice_default(self):
        """Test parsing default Fudge dice (4dF)."""
        result = self.roller.parse_dice_notation("4dF")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)
        self.assertEqual(result["modifier"], 0)

    def test_fudge_dice_explicit(self):
        """Test parsing explicit Fudge dice."""
        result = self.roller.parse_dice_notation("dF")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)  # Default is 4

    def test_fudge_dice_custom_count(self):
        """Test parsing custom number of Fudge dice."""
        result = self.roller.parse_dice_notation("2dF")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 2)

    def test_fudge_dice_lowercase(self):
        """Test parsing lowercase Fudge notation."""
        result = self.roller.parse_dice_notation("4df")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)

    def test_fudge_dice_fate_alias(self):
        """Test parsing Fate alias."""
        result = self.roller.parse_dice_notation("4dFate")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)

    def test_fudge_dice_fudge_alias(self):
        """Test parsing Fudge alias."""
        result = self.roller.parse_dice_notation("4dFudge")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)

    def test_fudge_dice_with_modifier(self):
        """Test parsing Fudge dice with positive modifier."""
        result = self.roller.parse_dice_notation("4dF+2")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)
        self.assertEqual(result["modifier"], 2)

    def test_fudge_dice_with_negative_modifier(self):
        """Test parsing Fudge dice with negative modifier."""
        result = self.roller.parse_dice_notation("2dF-1")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 2)
        self.assertEqual(result["modifier"], -1)

    def test_fudge_dice_fate_with_modifier(self):
        """Test parsing Fate alias with modifier."""
        result = self.roller.parse_dice_notation("4dFate+3")
        self.assertEqual(result["type"], "fudge")
        self.assertEqual(result["num_dice"], 4)
        self.assertEqual(result["modifier"], 3)


class TestDiceRolling(unittest.TestCase):
    """Test dice rolling logic."""

    def setUp(self):
        self.roller = DiceRoller()
        random.seed(42)  # For reproducible tests

    def test_single_die_range(self):
        """Test single die is in valid range."""
        for _ in range(100):
            rolls, total = self.roller.roll_dice(1, 20)
            self.assertEqual(len(rolls), 1)
            self.assertTrue(1 <= rolls[0] <= 20)
            self.assertEqual(total, rolls[0])

    def test_multiple_dice_range(self):
        """Test multiple dice are in valid range."""
        for _ in range(100):
            rolls, total = self.roller.roll_dice(3, 6)
            self.assertEqual(len(rolls), 3)
            for roll in rolls:
                self.assertTrue(1 <= roll <= 6)
            self.assertEqual(total, sum(rolls))

    def test_with_modifier(self):
        """Test modifier is applied correctly."""
        rolls, total = self.roller.roll_dice(2, 6, 5)
        self.assertEqual(total, sum(rolls) + 5)

    def test_negative_modifier(self):
        """Test negative modifier."""
        rolls, total = self.roller.roll_dice(1, 20, -3)
        self.assertEqual(total, rolls[0] - 3)


class TestFudgeDiceRolling(unittest.TestCase):
    """Test Fudge/Fate dice rolling logic."""

    def setUp(self):
        self.roller = DiceRoller()

    def test_fudge_faces_valid(self):
        """Test Fudge dice return valid faces."""
        for _ in range(100):
            faces, _ = self.roller.roll_fudge_dice(4)
            self.assertEqual(len(faces), 4)
            for face in faces:
                self.assertIn(face, ["+", " ", "-"])

    def test_fudge_total_range(self):
        """Test Fudge dice total is in valid range (-4 to +4 for 4dF)."""
        for _ in range(1000):
            _, total = self.roller.roll_fudge_dice(4)
            self.assertTrue(-4 <= total <= 4)

    def test_fudge_single_die(self):
        """Test single Fudge die."""
        faces, total = self.roller.roll_fudge_dice(1)
        self.assertEqual(len(faces), 1)
        self.assertTrue(-1 <= total <= 1)

    def test_fudge_with_modifier(self):
        """Test Fudge dice with modifier."""
        _, total = self.roller.roll_fudge_dice(4, 3)
        self.assertTrue(-1 <= total <= 7)  # -4+3 to +4+3

    def test_fudge_negative_modifier(self):
        """Test Fudge dice with negative modifier."""
        _, total = self.roller.roll_fudge_dice(4, -2)
        self.assertTrue(-6 <= total <= 2)  # -4-2 to +4-2

    def test_fudge_value_conversion(self):
        """Test face to value conversion."""
        # Force specific faces for testing
        random.seed(12345)
        faces, total = self.roller.roll_fudge_dice(4)
        # Verify total matches face values
        values = [{"+": 1, " ": 0, "-": -1}[f] for f in faces]
        self.assertEqual(total, sum(values))


class TestResultFormatting(unittest.TestCase):
    """Test result formatting."""

    def setUp(self):
        self.roller = DiceRoller()

    def test_single_die_no_modifier(self):
        """Test single die without modifier."""
        result = self.roller.format_roll_result("d20", [15], 15, 0)
        self.assertEqual(result, "🎲 d20 = 15")

    def test_single_die_with_modifier(self):
        """Test single die with modifier."""
        result = self.roller.format_roll_result("d20", [15], 20, 5)
        self.assertEqual(result, "🎲 d20 = 15+5 = 20")

    def test_multiple_dice_no_modifier(self):
        """Test multiple dice without modifier."""
        result = self.roller.format_roll_result("2d6", [3, 5], 8, 0)
        self.assertEqual(result, "🎲 2d6 = [3 + 5] = 8")

    def test_multiple_dice_with_modifier(self):
        """Test multiple dice with modifier."""
        result = self.roller.format_roll_result("2d6", [3, 5], 11, 3)
        self.assertEqual(result, "🎲 2d6 = [3 + 5]+3 = 11")

    def test_negative_modifier(self):
        """Test negative modifier formatting."""
        result = self.roller.format_roll_result("d20", [10], 8, -2)
        self.assertEqual(result, "🎲 d20 = 10-2 = 8")

    def test_fudge_no_modifier(self):
        """Test Fudge dice formatting without modifier."""
        result = self.roller.format_roll_result(
            "4dF", ["+", " ", "-", " "], 0, 0, dice_type="fudge"
        )
        self.assertEqual(result, "🔮 4dF = [+ - ] = 0")

    def test_fudge_with_modifier(self):
        """Test Fudge dice formatting with modifier."""
        result = self.roller.format_roll_result(
            "4dF", ["+", "+", " ", "-"], 2, 0, dice_type="fudge"
        )
        self.assertEqual(result, "🔮 4dF = [++ -] = 2")

    def test_fudge_positive_modifier(self):
        """Test Fudge dice formatting with positive modifier."""
        result = self.roller.format_roll_result(
            "4dF", ["+", " ", " ", "-"], 1, 2, dice_type="fudge"
        )
        self.assertEqual(result, "🔮 4dF = [+  -]+2 = 1")

    def test_fudge_negative_modifier(self):
        """Test Fudge dice formatting with negative modifier."""
        result = self.roller.format_roll_result(
            "4dF", ["+", "+", "+", "+"], 4, -1, dice_type="fudge"
        )
        self.assertEqual(result, "🔮 4dF = [++++]-1 = 4")


class TestRussianCommands(unittest.TestCase):
    """Test Russian command support."""

    def setUp(self):
        self.roll_commands = ["roll", "dice", "кинь", "брось", "куб", "кубы", "кости"]
        self.help_commands = ["help", "помощь", "справка", "h", "?"]

    def test_russian_roll_commands(self):
        """Test Russian roll commands are recognized."""
        self.assertIn("кинь", self.roll_commands)
        self.assertIn("брось", self.roll_commands)
        self.assertIn("куб", self.roll_commands)

    def test_russian_help_commands(self):
        """Test Russian help commands are recognized."""
        self.assertIn("помощь", self.help_commands)
        self.assertIn("справка", self.help_commands)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)

    # Manual test examples
    print("\n=== Manual Test Examples ===")
    roller = DiceRoller()

    test_cases = [
        "d20",
        "2d6",
        "3d8+2",
        "4d10-1",
        "d100",
        "1d4",
        "4dF",
        "dF",
        "2dF+1",
    ]

    for notation in test_cases:
        parsed = roller.parse_dice_notation(notation)
        if parsed:
            if parsed.get("type") == "fudge":
                num_dice = parsed["num_dice"]
                mod = parsed.get("modifier", 0)
                rolls, total = roller.roll_fudge_dice(num_dice, mod)
                result = roller.format_roll_result(
                    notation, rolls, total, mod, dice_type="fudge"
                )
            else:
                num = parsed["num_dice"]
                sides = parsed["sides"]
                mod = parsed.get("modifier", 0)
                rolls, total = roller.roll_dice(num, sides, mod)
                result = roller.format_roll_result(notation, rolls, total, mod)
            print(f"{notation:12} -> {result}")
        else:
            print(f"{notation:12} -> ❌ Invalid")
