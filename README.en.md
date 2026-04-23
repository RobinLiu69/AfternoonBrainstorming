# Afternoon Brainstorming Game Rules

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Static Badge](https://img.shields.io/badge/lang-en-red)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.en.md)
[![Static Badge](https://img.shields.io/badge/lang-zh.tw-blue)](https://github.com/RobinLiu69/AfternoonBrainstorming/blob/main/README.md)

## Game Overview
You will have 12 cards (built before the game starts). Each turn, you gain one attack opportunity (which can be saved for later). Use summoned minions or magic to gain an advantage.

Each active minion on the field (not paralyzed) scores one point for its owner. The scores offset each other, and the first player to lead their opponent by 10 points wins the game.

## Before the Game
![Screenshot_20241007_214036](https://github.com/user-attachments/assets/2c5819b8-a59d-4ed5-9383-99700cbd5b8c)

Build your 12-card deck. Each type of minion can be included up to twice, and each spell up to three times.

The first player selects 6 cards, then passes the selection to the next player (use the **E** key in two stages for toggling) to pick 12 cards. The first player then picks again. During selection, you can only see the opponent's first six cards.

> [!TIP]
> - **S** with the mouse position to select a card.
>
> - **A**, **D**: Previous / next page; **Space** can also be used for next page.
>
> - **C**: Clear the last selected card.
>
> - **E**: Toggle player (press once to hide both players' decks and show only the first 6 cards; press again to display the next player's deck).
>
> - **T**: Toggle timer.
>
> - **Y**: Decide whether to save the result chart.
>
> - **R**: Start the game (press twice).

## At the Start of the Game
![Screenshot_20241007_214217](https://github.com/user-attachments/assets/c43a401e-7ef3-4e99-9be7-cc68e746a586)

The first player (left side) starts with three cards in hand and one attack opportunity.

The second player starts their turn with four cards in hand and one attack opportunity.

> [!IMPORTANT]
> Both players can see each other's hands.
> Each turn, draw one card from your deck and gain one attack opportunity.

> [!NOTE]
> Attack opportunities are displayed as colored squares on both sides of the bottom: white, cyan, then red; each color represents 10 uses.

> [!TIP]
> - **1–9**, **0**: Place the corresponding card in your hand onto the grid at the mouse position (or cast a spell).
>
> - **Space**: Place the last card in your hand.
>
> - **A**: Attack.
>
> - **E**: End your turn.
>
> - The bottom area displays your deck and discard pile info. Minions that die or spell cards that are used go to the discard pile.

# Magic Cards
![Screenshot_20241007_215820](https://github.com/user-attachments/assets/55934318-f37a-413f-87b4-16635bc5582f)

- **Cubes (CUBES)**
  - After use, select two points on the board (keyboard **P**) to place small cubes (**CUBE**). They are neutral units with 4 HP and no attack power.

- **Heal (HEAL)**
  - Use the mouse with keyboard **H** to heal a unit for 6 HP. HP has a maximum value.

> [!NOTE]
> If any healing effect overflows the unit's maximum HP, every 2 points of overflow are converted into 1 point of shield.

- **Move (MOVE)**
  - After using this card, first select a friendly unit (keyboard **M**). That unit is then granted the **Moving** status, shown below its attack value.

> [!NOTE]
> Pressing **M** again on a Moving unit places it in the **Selected** state. Then choose an empty cell within the 3x3 grid around it and press **M** again to move the unit there.

> [!WARNING]
> Units in a paralyzed state cannot use Move.

# Effect Explanation
- **Numbness (Paralysis)**
  - The unit cannot attack, move, or score, but its own effects will still trigger.

> [!IMPORTANT]
> Units are given this effect when first placed, except for Assassins of all factions.

- **Armor**
  - Has no maximum value. When the unit is attacked, damage goes to the armor first until it reaches zero, then to HP.

> [!WARNING]
> Armor-break effects reduce armor directly to zero.

- **Moving**
  - A unit gains this status when a Move card is used on it.

> [!IMPORTANT]
> If both Moving and Numbness exist on a unit, it can still move.

> [!NOTE]
> If more than one unit has the Moving status on the field, use the mouse position and the **M** key to choose which one to move, granting it the **Selected** status.

- **Selected**
  - Used to decide which Moving unit will be moved.

- **Rage (Anger)**
  - This status's behavior depends on the specific unit's effect.

- **Luck Effects**
   - **Good Luck Effects**
     Each of the following five effects has a 20% chance of occurring:
       - Armor +4
       - Self attack x2
       - Attack once (based on the unit's attack pattern)
       - Grants the Moving effect
       - Places a lucky block in the X-shaped (diagonal) cells around its own position (no effect if triggered by the Green Mage)
   - **Bad Luck Effects**
     Each of the following five effects has a 20% chance of occurring:
       - Shield break
       - Gains the Numbness effect
       - HP halved
       - Attack halved
       - If HP is 2 or greater, HP is reduced by 2; otherwise no effect (does not trigger "on damaged" or "on killed" effects)

# Attack Types

- **Large Cross:** Attacks units in the same row and column.

- **Small Cross:** Attacks units directly adjacent (up, down, left, right).

- **Nine Grid:** Attacks units in the 3x3 grid around the attacker.

- **Diagonal Cross:** Attacks units diagonally (top-left, top-right, bottom-left, bottom-right).

- **Nearest Target:** Attacks the nearest single unit.

- **Farthest Target:** Attacks the farthest single unit.

# Faction Overview

![Screenshot_20241007_215700](https://github.com/user-attachments/assets/192971d8-e20d-4e2c-8b89-e6352705c007)

## White Faction

- **Triangle (ADC) - 5/4 - Large Cross**
- **Circle (AP) - 4/3 - Nearest Target** / Attack includes paralysis.
- **Square (TANK) - 15/1 - Small Cross**
- **Trapezoid (HF) - 9/2 - Nine Grid**
- **Double Diamond (LF) - 7/4 - Small Cross**
- **Assassin (ASS) - 2/5 - Diagonal Cross**
- **Hexagon (APT) - 8/2 - Nearest Target** / When attacking, grants itself and the nearest ally a shield equal to its own attack value.
- **Diamond (SP) - 1/5 - Farthest Target** / Gains one extra point per round.

## Red Faction

- **Triangle (ADC) - 4/2 - Large Cross** / Gains +1 attack after dealing damage.
- **Circle (AP) - 3/2 - Nearest Target** / Attack includes paralysis and steals 100% of the target's attack.
- **Square (TANK) - 9/1 - Small Cross** / Grants the nearest ally 2 points of shield when taking damage.
- **Trapezoid (HF) - 8/1 - Nine Grid** / Each time it deals damage, it loses 1 HP and gains 1 attack. This damage will not kill it directly; it is delayed until the end of the turn.
> [!IMPORTANT]
> It does not gain points.
- **Double Diamond (LF) - 6/2 - Small Cross** / Gains +1/+1 after dealing damage.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / After killing an enemy, grants the nearest ally +2 attack.
- **Hexagon (APT) - 6/2 - Nearest Target** / Grants +1/+1 to itself and the nearest ally when attacking.
- **Diamond (SP) - 1/5 - Farthest Target** / All buffs gained by Red-faction units are also stacked onto this unit.

## Green Faction

- **Triangle (ADC) - 3/3 - Large Cross** / After attacking, has a 50% chance to generate a lucky block within its attack range.
- **Circle (AP) - 3/2 - Nearest Target** / Attack includes paralysis and a random bad-luck effect, and gains a random good-luck effect or none. (See [Effect Explanation](#effect-explanation))
- **Square (TANK) - 9/1 - Small Cross** / After taking damage, applies a bad-luck effect or none to the attacker, depending on the enemy's luck value. (See [Effect Explanation](#effect-explanation))
- **Trapezoid (HF) - 8/1 - Nine Grid** / Destroying a block increases luck by 5% and places a lucky block at a random position.
- **Double Diamond (LF) - 6/3 - Small Cross** / Destroying a lucky block deals damage to the nearest enemy unit, with a 25% chance to refund the attack opportunity.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / After a kill, you gain 5% luck and the enemy loses 5% luck.
- **Hexagon (APT) - 5/0 - Nearest Target** / At the start of the turn, places lucky blocks on empty cells within its small-cross area. You gain 1 shield each time a friendly unit destroys a lucky block.
- **Diamond (SP) - ?/? - Farthest Target** / Increases luck by 10% and places (for every extra 10 luck) one lucky block at a random position. ~~(HP is definitely not 1, attack is definitely not 5)~~

> [!NOTE]
> **Green Special Unit**
>
> **Lucky Block (luckyblock) - 1/0** — Similar to a cube, but when forcibly destroyed it grants the destroying unit a random effect, based on the luck value of that unit's owner. (See [Effect Explanation](#effect-explanation))

## Blue Faction

- **Triangle (ADC) - 4/2 - Large Cross** / After drawing a card via blue tokens, it will auto-attack; if currently paralyzed, the paralysis is removed instead (no attack). Gains 2 blue tokens after a kill.
- **Circle (AP) - 4/2 - Nearest Target** / Attack includes paralysis and gains 2 blue tokens.
- **Square (TANK) - 10/1 - Small Cross** / Gains 1 blue token after taking damage.
- **Trapezoid (HF) - 8/2 - Nine Grid** / Attacks deal extra damage based on current blue tokens.
- **Double Diamond (LF) - 7/3 - Small Cross** / Gains 1 blue token after dealing damage.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / Gains 2 blue tokens after a kill.
- **Hexagon (APT) - 5/3 - Nearest Target** / Gains 1 shield whenever a blue token is gained. When attacking, gains 1 blue token for every 3 shield points.
- **Diamond (SP) - 1/5 - Farthest Target** / When placed, deals 1 damage to a random enemy, repeating (your discard pile + your field pile) times.

> [!NOTE]
> **Blue Token (token):** This value only applies to Blue decks. When the token count reaches 3, that player draws one card from the deck.

## Orange Faction

- **Triangle (ADC) - 4/2 - Large Cross** / Can move after attacking, and will auto-attack after moving.
- **Circle (AP) - 3/2 - Nearest Target** / Attack includes paralysis. At the start of the turn, gains one Move spell card usable that turn.
- **Square (TANK) - 10/1 - Small Cross** / After taking damage, gains one Move spell card usable that turn.
- **Trapezoid (HF) - 9/1 - Nine Grid** / Can move after attacking and gains +1 attack. The effect expires at end of turn.
- **Double Diamond (LF) - 6/3 - Small Cross** / Can move after attacking, and deals damage to the nearest target again.
- **Assassin (ASS) - 2/3 - Diagonal Cross** / Can move after a kill, and moving enters Rage (see [Effect Explanation](#effect-explanation)). While in Rage, killing an enemy refunds the attack opportunity and ends the Rage state.
- **Hexagon (APT) - 6/0 - Nearest Target** / When an ally moves, grants itself and the moving ally 1 shield. When it moves itself, shield is converted into attack at a 2:1 ratio.
- **Diamond (SP) - 1/5 - Farthest Target** / When an ally moves, deals 3 damage to the farthest target.

> ~~(Today 19:52: Have you finished eating yet?) (Today 21:22: Yeah, I finished...)~~

## Dark Green Faction (Totem Faction)

- **Triangle (ADC) - 4/2 - Large Cross** / Attacks deal additional damage equal to 1/4 of the totem.
- **Circle (AP) - 3/3 - Nearest Target** / Attack includes paralysis; attacks mark 5 layers on the totem.
- **Square (TANK) - 9/1 - Small Cross** / Marks 2 layers on the totem after taking damage.
- **Trapezoid (HF) - 8/2 - Nine Grid** / At the start of your turn, it takes 2 damage and marks 2 layers. Restores 1 HP after dealing damage.
- **Double Diamond (LF) - 6/3 - Small Cross** / When placed, deals 1/4-totem damage to enemies within its attack range; attacks gain 1 totem layer for each unit within the attack range.
- **Assassin (ASS) - 2/4 - Diagonal Cross** / Dies after a kill; each kill marks 7 layers on the totem.
- **Hexagon (APT) - 6/0 - Nearest Target** / When attacking, triggers in order: extra damage equal to 1/2 of the totem; gains totem layers equal to half of the shield gained; gains a shield equal to 1/2 of the damage dealt.
- **Diamond (SP) - 1/5 - Farthest Target** / While in play, totem marks are doubled.

## Cyan Faction (Pirate Faction)

- **Triangle (ADC) - 4/1 (6) - Large Cross** / Plunders 2$ after dealing damage / Double strike (+1/+2).
- **Circle (AP) - 3/1 (6) - Nearest Target** / Attacks paralyze the target and plunder 3$. On placement, attacks the nearest target 2 times (ignoring paralysis). / The 2 placement attacks are delegated: each one is performed by a random eligible ally — a friendly unit whose attack pattern contains `nearest` or `farthest` (i.e. AP, APT, or SP), other than itself and not paralyzed. The chosen ally uses its own attack pattern, but the target is forced to be AP's nearest enemy. If no eligible ally exists, AP performs the attack itself (+2/+2).
- **Square (TANK) - 9/1 (4) - Small Cross** / Gains 2$ when attacked / On its first attack, takes no damage (and does not trigger the enemy's effects) (+2/+0).
- **Trapezoid (HF) - 7/1 (6) - Nine Grid** / Plunders 2$ after dealing damage / Stays one extra turn after dying with +2 attack (+2/+1).
- **Double Diamond (LF) - 5/2 (4) - Small Cross** / Plunders 2$ after dealing damage / Gains a random attack pattern at the start of each turn (+2/+2).
- **Assassin (ASS) - 1/3 (4) - Diagonal Cross** / Plunders 6$ after a kill / +2 attack on the first attack (+1/+1).
- **Hexagon (APT) - 2/1 (6) - Nearest Target** / Every 5$ reduces incoming damage by 1 (up to 3) / Gains +4$ at the start of each turn (+5/+1).
- **Diamond (SP) - 1/2 (6) - Farthest Target** / Gains 10$ / While on the field, card costs are reduced by 2 (+1/+3).

> [!NOTE]
> **Coin (coin):** This value only applies to Cyan decks. Coins are used to evolve units. The number in parentheses after HP/attack is the coin cost to upgrade. You can hold up to 50 coins.
>
> The ability after the slash (`/`) is the extra ability granted after evolving. The unit keeps its original ability whether evolved or not. The last parenthesis shows the HP/attack bonus granted by evolution.

> [!IMPORTANT]
> Evolution can only be done while the card is in hand.
> Hover the mouse over the card you want to evolve and press the number key of its slot to complete the evolution. Evolution itself does not cost coins; coins are only spent when the card is placed.

## Fuchsia Faction (Shadow Faction)

> [!NOTE]
> **Shadow (shadow):** When a unit of this faction is placed (except Assassins), a shadow is spawned at the point-symmetric position (mirrored through the center). The shadow cannot be attacked, moved, or healed, and cannot be targeted by effects. When the main unit moves, the shadow moves to the corresponding position; when the main unit dies, the shadow disappears. Shadows on the field do not grant score.

> [!IMPORTANT]
> If there is a unit inside the shadow's attack area but not inside the main unit's attack area, the main unit can still attack correctly.

- **Triangle (ADC) - 4/2 - Large Cross** / When the main unit attacks, the shadow also attacks.
- **Circle (AP) - 4/1 - Nearest Target** / Attack includes paralysis. When placed and at the start of its turn, applies paralysis to enemies in the grid.
- **Square (TANK) - 10/1 - Small Cross** / Units cannot be placed on the shadow's position.
- **Trapezoid (HF) - 8/1 - Nine Grid** / When the main unit attacks, the shadow also attacks.
- **Double Diamond (LF) - 6/2 - Small Cross** / When attacking an enemy, deals damage to the nearest enemy from the shadow's position. If the main unit and the shadow both damage the same unit, it takes one more hit.
- **Assassin (ASS) - 2/3 - Diagonal Cross** / After a kill, places an immobile shadow at the killed enemy's position; when the main unit attacks, the shadow also attacks.
- **Hexagon (APT) - 5/3 - Nearest Target** / Friendly units on top of the shadow take 50% less damage, and the reduced damage is converted into a shield applied to itself.
- **Diamond (SP) - 1/5 - Farthest Target** / When placed, spawns a copy of the farthest ally's shadow (this shadow cannot move).

## Purple Faction

- **Circle (AP) - 3/1 - Nearest Target** / When placed, breaks the shield of the nearest unit you don't control and reduces its attack to its original value. The same effect applies when this unit attacks, additionally applying paralysis.
- **Square (TANK) - 9/1 - Small Cross** / Enemies lose 2 HP after moving.
> [!IMPORTANT]
> This faction's units are not nullified by paralysis-immunity effects.
- **Assassin (ASS) - 2/3 - Diagonal Cross** / After a kill, draws (enemy field pile − your field pile − 2) cards.
- **Trapezoid (HF) - 8/1 - Nine Grid** / At the start of its turn, counts all enemy units (excluding neutral units) within its attack range, and gains (that number / 3) attack opportunities.

# Endgame Summary Screen

## Player Score Display
![Screenshot_20241007_214359](https://github.com/user-attachments/assets/a71dd9fe-2aa4-4d0f-92c8-9d00ca980e8f)

## Player Data Chart Display
![Screenshot_20241007_214542](https://github.com/user-attachments/assets/844ffd88-eb28-4360-b78d-275cf2fd9287)

## Both-Player Table Display
![Screenshot_20241007_214508](https://github.com/user-attachments/assets/4f354a9e-369b-43cb-b3e4-65a5501633d8)

> [!TIP]
> Use **Tab** to view data for both players — Player 1's data is on top, Player 2's data is on the bottom.
> Use number keys **1**, **2**, and **SPACE** to toggle between player charts.
> Press **ESC** to exit.

## Data Explanation
**KDA:** Kills / Deaths

**Average Attack Damage:** Total damage dealt / Number of attacks

**Per Round Influence:** (Damage dealt × Damage received) / Rounds survived

**Survival Index:** ((Score × 2) + (Damage dealt / Number of attacks × 2) + (Damage received / Times hit × 2)) / Rounds survived

## License

Copyright (C) 2024 Robin Liu, Angus Yu / Five O'clock Shadow Studio

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
[GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.html)
for more details.

See [LICENSE.txt](./LICENSE.txt) for the full license text.

> **Note:** Game assets (images, fonts, sounds) are © 2024 Robin Liu / Five O'clock Shadow Studio.
> All rights reserved unless otherwise stated.

# External Links
[Rules on Bahamut](https://home.gamer.com.tw/artwork.php?sn=5702820)
> [!CAUTION]
> The rules in this README take precedence!

[Godot Version](https://github.com/AaronCheng1996/AfternoonBrainstorming_godot)