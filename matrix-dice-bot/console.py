#!/usr/bin/env python3
"""
Console interface for testing dice rolls without Matrix connection.
Allows manual testing of dice notation parsing and rolling.
Uses shared DiceRoller from dice_roller.py module.
"""

import sys

sys.path.append("/home/isaac/Repos/bs/proj/matrix-dice-bot")
from dice_roller import DiceRoller


def print_welcome():
    """Print welcome message."""
    print("=" * 60)
    print("🎲 Matrix Dice Bot - Консольный режим")
    print("=" * 60)
    print()
    print("Доступные форматы:")
    print("  d20, d6, d8, d10, d12, d100 - стандартные кубы")
    print("  dF, dFudge, dFate - кубы Fudge/Fate (4 куба по умолчанию)")
    print("  2d6, 3d8+2, 4d10-1 - с количеством и модификатором")
    print()
    print("Команды:")
    print("  !roll <кубы>  - бросить кубы")
    print("  !r <кубы>  - бросить кубы")
    print("  !кинь <кубы>  - русская команда")
    print("  !брось <кубы> - русская команда")
    print("  help          - показать эту справку")
    print("  quit, exit    - выход")
    print()
    print("Примеры:")
    print("  !roll d20     - один куб d20")
    print("  !roll 2d6     - два куба d6")
    print("  !roll 4dF     - четыре куба Fudge")
    print("  !roll dF      - четыре куба Fudge (по умолчанию)")
    print("  !roll 1dF     - один куб Fudge (явно указано)")
    print()
    print("=" * 60)


def extract_dice_notation(command: str) -> str:
    """Extract dice notation from command string."""
    command = command.strip()

    # Remove command prefix if present
    prefixes = ["!roll ", "!кинь ", "!брось ", "/roll ", "!r "]
    for prefix in prefixes:
        if command.lower().startswith(prefix):
            return command[len(prefix) :]

    # If no prefix, return as-is
    return command


def main():
    """Main console loop."""
    roller = DiceRoller()
    print_welcome()

    while True:
        try:
            command = input("\n🎲 > ").strip()

            if not command:
                continue

            if command.lower() in ["quit", "exit", "q"]:
                print("До свидания! 🎲")
                break

            if command.lower() in ["help", "h", "?"]:
                print_welcome()
                continue

            # Extract dice notation from command
            dice_notation = extract_dice_notation(command)

            # Use shared DiceRoller to process the roll
            result = roller.process_roll(dice_notation)

            if result:
                print(result)
            else:
                print(f"❌ Нераспознанная команда: {command}")
                print("Введите 'help' для списка доступных команд")

        except KeyboardInterrupt:
            print("\nДо свидания! 🎲")
            break
        except EOFError:
            print("\nДо свидания! 🎲")
            break


if __name__ == "__main__":
    main()
