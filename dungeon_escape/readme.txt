====================================================================
DUNGEON ESCAPE
====================================================================

1. DESCRIPTION
--------------
Dungeon Escape is a 2D top-down roguelike game built with Pygame Zero.
The player must explore the dungeon, avoid dangerous patrolling creatures,
collect all 5 magical crystals to unlock the portal, and escape safely.


2. LIBRARIES USED
-----------------
- Pygame Zero (pgzero)
- math (Python Standard Library)
- random (Python Standard Library)

No other external libraries or frameworks are used.
(No direct pygame imports).


3. HOW TO RUN THE GAME
----------------------
1. Install Pygame Zero (if not already installed):
   pip install pgzero

2. Open a terminal, enter the project folder, and run:
   cd dungeon_escape
   pgzrun main.py


4. CONTROLS
-----------
- Move:  W, A, S, D  or  Arrow Keys
- Menu:  Click buttons with Mouse (or press Space on Main Menu)


5. HOW TO PLAY
--------------
- Start the game from the Main Menu.
- Avoid the 4 dangerous dungeon creatures (Slime, Skeleton Warrior, 
  Dungeon Ghost, and Skeleton Guardian). Each creature patrols its own 
  territory and can damage the player.
- You have 3 lives. Taking damage grants a 1-second invulnerability cooldown.
- Collect all 5 cyan crystals scattered across the dungeon room.
- Once all 5 crystals are gathered, the exit portal at the top unlocks.
- Touch the active portal to escape and win!
- If you lose all 3 lives, the game ends in a defeat screen.
- You can restart or return to the main menu at any time.


6. CREDITS
----------
- Code & Systems: Python OOP Assessment Project (Student Tutor Test).
- Assets & Sounds: CC0 Public Domain assets & procedural audio.
====================================================================
