# Chess RPG

### Key Mechanics
* **Action Economy:** Each piece generally has $1$ Move action and $1$ Combat action per turn.
* **Combat & Retaliation:** When a piece attacks an opponent, the target will immediately counter-attack (retaliate) if the attacker stands within its attack range.
* **Healing:** Instead of attacking, a piece can spend its combat action to heal itself for **40% of its missing health**.
* **Undo System ($Z$ Key):** Made a mistake? Players can roll back up to $5$ actions during their turn.

---

## Unit Archetypes

Each piece on the board behaves differently and possesses a unique trait described in the game's user interface:

| Piece | Specialty / Ability Description |
| :--- | :--- |
| **Pawn (Pėstininkas)** | Gaining a kill grants $+1$ maximum health and completely heals the unit. |
| **Rook (Bokštas)** | **Taunt Aura:** Any adjacent enemy piece is forced to target the Rook if they choose to attack. |
| **Knight (Žirgas)** | **Blitz:** Securing a kill completely refreshes the Knight's move and combat counters, allowing it to act again. |
| **Bishop (Rikis)** | **Cleave & Push:** Attacks up to 3 tiles at once diagonally. Attacks knock enemies backward and push the Bishop away from the target. |
| **Queen (Karalienė)** | **Shadowstep:** After an attack, the Queen automatically teleports next to the attacked piece. Can also use its attack range dynamically for movement. |
| **King (Karalius)** | **High Value:** The heart of the army. If your King dies, the game is immediately lost. |

---

## Controls

### Army Draft Phase

Before the battle begins, players enter an interactive drafting phase to customize and assemble their army. You start with a budget of **38 total points** to spend on buying units.

```text
       [ RED ZONE: Enemy Territory - Cannot Place Units ]
  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
       [ GREEN ZONE: Deployment Phase - Place Units Here ]
```

Selection Rules & Visual Indicators

The King is Free: A King is automatically and randomly generated on the board for you at the start of the draft without consuming points.

Deployment Grid: The board is split into two regions during this phase. You can only spawn troops inside your designated green deployment zone (the bottom 3 rows, where row index > 4).

Refund System: Made a mistake or changed your mind? Clicking an existing friendly unit with the Left Mouse Button (LMB) will instantly dismiss it and fully refund its point value back to your pool.

Drafting Controls: To place a unit, hover your mouse cursor over an empty tile within the green zone and press the corresponding hotkey:

| Key | Unit Type | Point Cost |
| :---: | :--- | :--- |
| **`K`** | Queen (Karalienė) | 9 Points |
| **`B`** | Rook (Bokštas) | 4 Points |
| **`R`** | Bishop (Rikis) | 3 Points |
| **`Z`** | Knight (Žirgas) | 3 Points |
| **`P`** | Pawn (Pėstininkas) | 1 Point |
| **`LMB`** | Remove Unit | Full Refund |
| **`ENTER`** | Confirm Army | Starts Battle |

### In-Game Controls

* `Left Mouse Button (LMB)`: Select a piece / Confirm a movement, attack, or heal target.
* `Right Mouse Button (RMB)`: Cancel current action state or return to movement selection mode.
* `1` Key: Switch the selected piece to **Attack Mode** (shows red attack indicators).
* `2` Key: Switch the selected piece to **Heal Mode** (shows green healing numbers over the piece).
* `Z` Key: **Undo** last action (Usable up to 5 times per turn).
* `ENTER` Key: Confirm undo actions / Manually end your current turn.

---

## Installation & Running the Game

### Prerequisites
Have `Python 3.x` installed along with the `pygame` library.

Project Structure: Ensure your local directory includes a Graphics/ folder containing the required .png sprites named exactly in the "{Team} {Piece}.png" format (e.g., Graphics/White Pawn.png, Graphics/Black King.png).

```text
├── main.py            # Main game executable code
└── Graphics/          # Asset folder
    ├── White Pawn.png
    ├── White Rook.png
    ├── Black King.png
    └── ... (other pieces)
```

Run the Game:

```text
python main.py
```
