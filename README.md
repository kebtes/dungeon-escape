# Dungeon Escape ⚔️

A polished 2D top-down roguelike game built with **Python** and **Pygame Zero**.

---

## 🎮 How to Run

1. **Install Pygame Zero** (if not installed):
   ```bash
   pip install pgzero
   ```

2. **Navigate into the game folder and run**:
   ```bash
   cd dungeon_escape
   pgzrun main.py
   ```

---

## 🕹️ Controls

- **Movement**: `W`, `A`, `S`, `D` or `Arrow Keys`
- **Interface**: Mouse clicks on menu buttons (or `Space` to start)

---

## 📜 How to Play

- **Objective**: Collect all **5 magical crystals** to unlock the escape portal, then reach the portal to win.
- **Enemies**: 4 dangerous creatures patrol their own territories (Slime, Skeleton Warrior, Dungeon Ghost, and Skeleton Guardian). Avoid them!
- **Health**: You have 3 lives. Colliding with an enemy deals 1 damage with a 1-second invulnerability cooldown and knockback.
- **Audio**: You can toggle music and sound effects on/off from the Main Menu.

---

## 🛠️ Technical Details & Libraries

- **Engine**: Pygame Zero (`pgzero`)
- **Allowed Standard Modules**: `math`, `random`
- **Architecture**: Object-Oriented Programming (`Player`, `Enemy`, `Button` classes)
- **Zero Prohibited Libraries**: No `pygame` imports, no external game engines.
