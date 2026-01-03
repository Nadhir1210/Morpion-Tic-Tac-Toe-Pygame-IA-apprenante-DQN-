"""tictactoe_env.py

Environnement Morpion (Tic-Tac-Toe) indépendant de l'interface Pygame.

- État: plateau 3x3 encodé en liste de 9 entiers: 0 (vide), 1 (joueur courant), -1 (adversaire)
- Actions: indices 0..8

Ce module est volontairement simple pour être réutilisé:
- entraînement DQN (self-play)
- conversion plateau Pygame -> état numérique

Aucune donnée externe: les épisodes sont générés en jouant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


WIN_COMBOS: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def check_winner(board_abs: List[int]) -> int:
    """Retourne 1 si X gagne, -1 si O gagne, 0 sinon.

    Ici, `board_abs` utilise la convention absolue: 1 pour X, -1 pour O, 0 vide.
    """
    for a, b, c in WIN_COMBOS:
        s = board_abs[a] + board_abs[b] + board_abs[c]
        if s == 3:
            return 1
        if s == -3:
            return -1
    return 0


def is_draw(board_abs: List[int]) -> bool:
    return all(v != 0 for v in board_abs) and check_winner(board_abs) == 0


def valid_actions(board_abs: List[int]) -> List[int]:
    return [i for i, v in enumerate(board_abs) if v == 0]


def to_perspective(board_abs: List[int], player: int) -> List[int]:
    """Convertit un plateau absolu vers la perspective du joueur courant.

    - `player` vaut 1 (X) ou -1 (O)
    - sortie: 1 = mes pions, -1 = adversaire, 0 = vide
    """
    return [v * player for v in board_abs]


def from_chars(plateau_chars: List[str], agent_symbol: str) -> Tuple[List[int], int]:
    """Convertit un plateau en chars ['X','O',' '] vers plateau absolu int.

    Returns:
        (board_abs, agent_player)
        - board_abs: 1 pour X, -1 pour O, 0 vide
        - agent_player: 1 si l'agent joue X, -1 si l'agent joue O
    """
    board_abs: List[int] = []
    for c in plateau_chars:
        if c == 'X':
            board_abs.append(1)
        elif c == 'O':
            board_abs.append(-1)
        else:
            board_abs.append(0)

    agent_player = 1 if agent_symbol == 'X' else -1
    return board_abs, agent_player


@dataclass
class Transition:
    state: List[float]
    action: int
    reward: float
    next_state: List[float]
    done: bool
    next_valid_mask: List[float]
