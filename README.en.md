# Afternoon Brainstorming Game Rules

[![Static Badge](https://img.shields.io/badge/lang-en-red)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.en.md)  [![Static Badge](https://img.shields.io/badge/lang-zh.tw-blue)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.md)

## Game Overview  
You will have 12 cards (Chose before the game starts). Each turn, you gain one attack opportunity (which can be saved for later). Use summoned minions or magic to gain an advantage.  

Each active minion on the field (not stunned) scores one point for its owner. The scores offset each other, and the first player to lead their opponent by 10 points wins the game.  

## Before the Game  
![Screenshot_20241007_214036](https://github.com/user-attachments/assets/2c5819b8-a59d-4ed5-9383-99700cbd5b8c)  

Choose your 12 cards. Each type of minion can be included up to twice, and each spell up to three times.  

The first player selects 6 cards, then passes the selection to the next player (use the **E** key for toggling). After both players select their 12 cards, the game starts. During selection, you can only see the opponent's first six cards.  

> [!TIP]
> - Use **S** and the mouse to select cards.  
> - **A**, **D**: Navigate pages; use the **Space** key for next page.  
> - **C**: Clear the last selected card.  
> - **E**: Toggle player (press once to hide both players' decks and show the first 6 cards; press again to display the next player's deck).  
> - **T**: Toggle timer.  
> - **Y**: Decide whether to save the result chart.  
> - **R**: Start the game (press twice).  

## At the Start of the Game  
![Screenshot_20241007_214217](https://github.com/user-attachments/assets/c43a401e-7ef3-4e99-9be7-cc68e746a586)  

The first player (left side) starts with three cards in hand and one attack opportunity.  

The second player starts their turn with four cards in hand and one attack opportunity.  

> [!IMPORTANT]
> Both players can see each other's hands.  
> Each turn, draw one card from your deck and gain one attack opportunity.  

> [!NOTE]
> Attack opportunities are displayed as colored squares in the bottom corner: First, when attack opportunity is under 10 or equal will be displayed in white, then blue, then red.

> [!TIP]
> - Press **1–9**, **0** to place the corresponding card in your hand onto the board at the mouse position (or cast a spell).  
> - **Space**: Place the last card in your hand.  
> - **A**: Attack.  
> - **E**: End your turn.  
> - The bottom area displays your deck and discard pile card infos. Minions that die or used spell cards go to the discard pile.  

---

### Magic Cards  
![Screenshot_20241007_215820](https://github.com/user-attachments/assets/55934318-f37a-413f-87b4-16635bc5582f)  

- **Cubes**  
  - Place two small cubes (neutral units with 4 HP and no attack) on the board by selecting two points using **P**.  

- **Heal**  
  - Use **H** to heal a unit by 5 HP (health has a maximum value).  

> [!NOTE]
> If healing exceeds the maximum HP, the excess is converted into shields at a 2:1 ratio.  

- **Move**  
  - Select a friendly unit (**M**) to grant it a "Moving" effect, displayed below its attack value.  

> [!NOTE]
> Press **M** again on a moving unit to mark it as "Selected". Then choose an empty spot which are in a 3x3 grid around the unit on the board and press **M** to move the unit there.  

> [!WARNING]
> Units in a stunned state cannot move.  

---

### Status Effects  

- **Numbness** (Stun)  
  - The unit cannot attack, move, or score, but its effects still trigger.  

> [!IMPORTANT]
> Units gain this effect upon placement, except for Assassins.  

- **Armor**  
  - Absorbs damage before it reaches HP. Armor has no maximum limit and is reduced to zero before HP is affected.  

> [!WARNING] 
> Effects that break armor reduce it directly to zero.  

- **Moving**  
  - A unit gains this status when the Move card is used on it.  

> [!IMPORTANT]
> Moving units can still move even if they are stunned.  

> [!NOTE]
> If multiple units are moving, use the mouse and **M** to select one, applying the "Selected" effect.  

- **Selected**  
  - Identifies which moving unit will be moved next.  

- **Rage** (Anger)  
  - This status triggers effects specific to the unit.


- **Luck Effects**
   - **Good Luck Effects**
     The following five effects have a 20% chance each of occurring:
       - Armor +4
       - Attack damage x2
       - Attack once (based on the unit's attack type)
       - Adds a "moving" effect
       - Places one lucky block above, below, left, and right of the current lucky block. (No effect if this applies to the Green Mage unit)
   - **Bad Luck Effects**
     The following five effects have a 20% chance each of occurring:
       - Shield break
       - Gains a stun effect
       - HP halved
       - Attack halved
       - If HP is greater than or equal to 2, it is reduced by 2. Otherwise, no effect. (Does not trigger effects related to being attacked or killed)

# Attack Types

- **Large Cross:** Attacks units in the same row and column.
- **Small Cross:** Attacks units directly adjacent (up, down, left, right).
- **Nine Grid:** Attacks units in a 3x3 grid around the attacker.
- **Diagonal Cross:** Attacks units diagonally (top-left, top-right, bottom-left, bottom-right).
- **Closest Single Unit:** Attacks the nearest unit.
- **Furthest Single Unit:** Attacks the furthest unit.

# Faction Overview

## White Faction
![Screenshot](https://github.com/user-attachments/assets/192971d8-e20d-4e2c-8b89-e6352705c007)

- **Triangle (ADC) - 5/4 - Large Cross**
- **Circle (AP) - 4/3 - Nearest Target** / Paralyzes on attack.  
- **Square (TANK) - 15/1 - Small Cross**
- **Trapezoid (HF) - 9/2 - Nine Grid**
- **Double Diamond (LF) - 7/3 -Small Cross**
- **Assassin (ASS) - 2/5 - Diagonal Cross**
- **Hexagon (APT) - 8/2 - Nearest Target** / Provides 2 points of shield to self and nearest ally upon attack.  
- **Diamond (SP) - 1/5 - Farthest Target** / Gains an extra point each round.  

## Red Faction
![Screenshot](https://github.com/user-attachments/assets/102ae8a6-988a-4332-8214-2ea4582e0ecd)

- **Triangle (ADC) - 4/1 - Large Cross** / Gains +1 attack after dealing damage.  
- **Circle (AP) - 3/2 - Nearest Target** / Paralyzes and steals 100% of the target's attack.  
- **Square (TANK) - 9/1 - Small Cross** / Provides 2 points of shield to the nearest ally when taking damage.  
- **Trapezoid (HF) - 9/1 - Nine Grid** / Loses 1 HP after dealing damage, gains 1 attack, and cannot die directly from this damage (delayed until end of turn).  
> [!IMPORTANT]  
> Does not gain points, when it's HP below 1.  
- **Double Diamond (LF) - 5/2 - Small Cross** / Gains +1/+1 after dealing damage.  
- **Assassin (ASS) - 2/4 - Diagonal Cross** / Grants the nearest ally +2 attack after killing an enemy.  
- **Hexagon (APT) - 6/2 - Nearest Target** / Grants +1/+1 to self and nearest ally when attacking.  
- **Diamond (SP) - 1/2 - Farthest Target** / All buffs gained by Red units are also transferred to this unit.

## Green Faction
![Screenshot_20241007_215718](https://github.com/user-attachments/assets/21980993-b2d8-4a5b-a61e-5a8296f2ab52)

- **Triangle (ADC) - 3/3 - Large Cross** / After attack, there is a 50% chance to spawn a lucky block for each block in the attack range.
- **Circle (AP) - 3/2 - Nearest Target** / Attack includes paralysis and, based on the enemy's luck value, causes a random bad luck effect. Additionally, based on your own luck value, it causes a random good luck effect or none. (See [Effect Explanation](#effect-explanation))
- **Square (TANK) - 10/1 - Small Cross** / After taking damage, a bad luck effect or none is applied to the attacker, depending on their luck effect. (See [Effect Explanation](#effect-explanation))
- **Trapezoid (HF) - 8/1 - Nine Grid** / Destroying blocks increases luck by 5% and randomly places a lucky block on the board.
- **Double Diamond (LF) - 6/2 - Small Cross** / Destroying a lucky block deals 4 damage to the nearest enemy, with a 25% chance to return a attack opportunity.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / After killing an enemy, you gain 5% luck, and the enemy loses 5% luck.
- **Hexagon (APT) - 6/0 - Nearest Target** / After attacking, it places a lucky block in the small cross area, and it gains 1 shield for each lucky block placed in the rest of the game.
- **Diamond (SP) - ?/? - Farthest Target** / When it enters, increases luck by 10% and randomly places lucky blocks based on the luck value (for every 10 luck, one lucky block is placed).

> [!NOTE]
> **Green Special Unit**
>
> **Lucky Block (LuckyBlock) - 1/0** - Similar to a block but will cause random effects on the unit that destroys it, depending on the unit owner's luck value. (See [Effect Explanation](#effect-explanation))

## **Blue Faction**
![Screenshot_20241007_215726](https://github.com/user-attachments/assets/c1934832-6e5a-439a-8635-54fcca8ed202)

- **Triangle (ADC) - 4/2 - Large Cross** / Automatically attacks after using blue balls to drawing a card. If the unit is paralyzed, it will remove the paralysis but not attack. After dealing damage, gains 1 blue ball.
- **Circle (AP) - 4/2 - Nearest Target** / Attack includes paralysis and gains 2 blue balls.
- **Square (TANK) - 10/1 - Small Cross** / After taking damage, gains 1 blue ball.
- **Trapezoid (HF) - 8/2 - Nine Grid** / Attack deals additional damage based on the number of blue balls.
- **Double Diamond (LF) - 6/3 - Small Cross** / After dealing damage, gains 1 blue ball.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / After killing an enemy, gain 2 blue balls.
- **Hexagon (APT) - 5/3 - Nearest Target** / Gaining a blue ball also grants 1 shield. When attacking, for every 4 points of shield, 1 blue ball is gained.
- **Diamond (SP) - 1/5 - Farthest Target** / When placed, it deals 1 point of damage to a random enemy, repeating based on the number of cards in your discard pile and on the field.

> [!NOTE]
> **Blue Token (Blue Ball):** This value only applies to blue units. When it reaches 3, the player will draw a card from the deck.

## **Orange Faction**
![Screenshot_20241007_215736](https://github.com/user-attachments/assets/44312b89-eb8b-4a29-bb38-9680e0aeb94c)

- **Triangle (ADC) - 4/2 - Large Cross** / After attacking, can move and will automatically attack again after moving.
- **Circle (AP) - 3/2 - Nearest Target** / Attack includes paralysis, and at the start of the turn, it gains a usable movement magic card for the turn.
- **Square (TANK) - 10/1 - Small Cross** / After taking damage, gains a usable movement magic card for the turn.
- **Trapezoid (HF) - 9/1 - Nine Grid** / After attacking, can move and gains +1 attack. The effect disappears after the turn ends.
- **Double Diamond (LF) - 6/3 - Small Cross** / After attacking, can move and deal damage to the nearest target again.
- **Assassin (ASS) - 2/3 - Diagonal Cross** / After killing an enemy, can move and enter a rage state (See [Effect Explanation](#effect-explanation)). In rage mode, killing enemies will return the attack opportunity and remove the rage state.
- **Hexagon (APT) - 6/0 - Nearest Target** / After a teammate moves, both itself and the moving ally gain 1 shield. If itslef moves, the shield is converted into attack at a 2:1 ratio.
- **Diamond (SP) - 1/5 - Farthest Target** / After a teammate moves, deals 3 points of damage to the farthest target.

## **Dark Green Faction**
![Screenshot_20241007_220122](https://github.com/user-attachments/assets/a015caca-21ca-40e8-9014-b62f266887d0)

- **Triangle (ADC) - 4/1 - Long Cross** / Deals additional 1/4 damage from the totem when attacking.
- **Circle (AP) - 3/3 - Nearest Target** / After attacking, marks 5 layers of the totem.
- **Square (TANK) - 9/1 - Small Cross** / After taking damage, marks 2 layers of the totem.
- **Trapezoid (HF) - 8/2 - Nine Grid** / At the start of the owner's turn, it takes 2 damage and marks 2 layers of the totem. After dealing damage, it restores 1 health point.
- **Double Diamond (LF) - 6/3 - Small Cross** / Upon placement, deals 1/4 damage to all enemies in the attack range, and the attack marks 1 layer of the totem for each unit within the range.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / After killing an enemy, it dies. Each kill marks 4 layers of the totem.
- **Hexagon (APT) - 6/0 - Nearest Target** / When attacking, it triggers additional damage of 1/2 from the totem, gains shield based on half the layers of the totem, and gains shield equal to half of the damage dealt.
- **Diamond (SP) - 1/5 - In-play effect** / Doubles the mark count of all units in play.

### **Purple Faction**
![Screenshot_20241007_215754](https://github.com/user-attachments/assets/59a60549-3eba-427d-9564-4251818eaa79)

- **Circle (AP) - 3/1 - Nearest Target** / Attack includes paralysis, breaks shields, and reduces the target's attack to its original value.
- **Square (TANK) - 9/1 - Small Cross** / After the enemy moves, they lose 2 health points.
> [!IMPORTANT]
> This faction's units are not affected by paralysis immunity effects.
- **Assassin (ASS) - 2/3 - Diagonal Cross** / After a kill, draws a number of cards based on the difference between the enemy and (player field piles + 3).
- **Trapezoid (HF) - 8/1 - Nine Grid** / At the start of the player's turn, calculates all the enemy units in its attack range (excluding neutral units), and add an attack opportunity for every 3 enemies.

# Endgame Summary Screen

## Player Score Display
![Screenshot](https://github.com/user-attachments/assets/a71dd9fe-2aa4-4d0f-92c8-9d00ca980e8f)

## Player Data Chart Display
![Screenshot](https://github.com/user-attachments/assets/844ffd88-eb28-4360-b78d-275cf2fd9287)

## Player Table Display
![Screenshot](https://github.com/user-attachments/assets/4f354a9e-369b-43cb-b3e4-65a5501633d8)

> [!TIP]  
> Use **Tab** to view data for both players. Player 1's data is on top, Player 2's is below.  
> Use **keys** **1**, **2**, **SPACE** to toggle between player charts.  
> Press **ESC** to exit.

## Data Explanation
- **KDA:** Kills / Deaths  
- **Average Attack Damage:** Total damage dealt / Number of attacks  
- **Per Round Influence:** (Damage dealt × Damage received) / Rounds survived  
- **Survival Index:** ((Score × 2) + (Damage dealt / Attacks × 2) + (Damage received / Times hit × 2)) / Rounds survived  

# External Links
[Rules on Bahamut](https://home.gamer.com.tw/artwork.php?sn=5702820)  
> [!CAUTION]  
> Rules on this page take precedence!

[Godot Version](https://github.com/AaronCheng1996/AfternoonBrainstorming_godot)

 
