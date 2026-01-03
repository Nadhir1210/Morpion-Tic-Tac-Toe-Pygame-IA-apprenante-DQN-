"""dqn_agent.py

Deep Q-Network (DQN) pour Morpion 3x3.

Contraintes couvertes:
- PyTorch (réseau de neurones)
- Experience Replay
- ε-greedy exploration
- Récompenses: +1 victoire, -1 défaite, 0 match nul
- Pas de dataset externe: toutes les transitions sont générées par le jeu (self-play ou vs humain)

Remarque:
- Ce DQN est volontairement "simple" pour un projet académique.
- Améliorations recommandées (Target Network, Double DQN, sauvegarde) sont faciles à ajouter.
"""

from __future__ import annotations

import os
import random
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.optim as optim

from tictactoe_env import Transition, check_winner, is_draw, to_perspective, valid_actions


# =====================
# Paramètres principaux
# =====================
# Modifie ces valeurs pour tes expérimentations (rapport/PFE).

# Hyperparamètres DQN
DEFAULT_GAMMA = 0.99
DEFAULT_LR = 1e-3
DEFAULT_BATCH_SIZE = 64
DEFAULT_REPLAY_CAPACITY = 50_000
DEFAULT_MIN_REPLAY_SIZE = 1_000

# Exploration ε-greedy
DEFAULT_EPSILON_START = 1.0
DEFAULT_EPSILON_END = 0.05
DEFAULT_EPSILON_DECAY_STEPS = 30_000

# Nombre de mises à jour (gradient steps) par coup joué
DEFAULT_TRAIN_STEPS_PER_MOVE = 1

# Target Network: fréquence de mise à jour (hard update)
DEFAULT_TARGET_UPDATE_INTERVAL = 500

# Entraînement self-play: nombre d'épisodes par défaut
DEFAULT_SELF_PLAY_EPISODES = 3000

# Bootstrap au premier lancement (si aucun modèle n'existe encore)
DEFAULT_BOOTSTRAP_EPISODES = 2500


class QNetwork(nn.Module):
    def __init__(self, input_size: int = 9, hidden: int = 64, output_size: int = 9):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ReplayBuffer:
    def __init__(self, capacity: int = 50_000):
        self.buffer: Deque[Transition] = deque(maxlen=capacity)

    def __len__(self) -> int:
        return len(self.buffer)

    def push(self, transition: Transition) -> None:
        self.buffer.append(transition)

    def sample(self, batch_size: int) -> List[Transition]:
        return random.sample(self.buffer, batch_size)


@dataclass
class DQNConfig:
    gamma: float = DEFAULT_GAMMA
    lr: float = DEFAULT_LR
    batch_size: int = DEFAULT_BATCH_SIZE
    replay_capacity: int = DEFAULT_REPLAY_CAPACITY
    min_replay_size: int = DEFAULT_MIN_REPLAY_SIZE

    # Target Network (stabilisation)
    target_update_interval: int = DEFAULT_TARGET_UPDATE_INTERVAL  # hard update every N gradient steps

    epsilon_start: float = DEFAULT_EPSILON_START
    epsilon_end: float = DEFAULT_EPSILON_END
    epsilon_decay_steps: int = DEFAULT_EPSILON_DECAY_STEPS

    train_steps_per_move: int = DEFAULT_TRAIN_STEPS_PER_MOVE


class DQNAgent:
    def __init__(
        self,
        config: Optional[DQNConfig] = None,
        device: Optional[str] = None,
    ):
        self.config = config or DQNConfig()
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        self.q = QNetwork().to(self.device)
        self.q_target = QNetwork().to(self.device)
        self.q_target.load_state_dict(self.q.state_dict())
        self.q_target.eval()
        self.optimizer = optim.Adam(self.q.parameters(), lr=self.config.lr)
        self.loss_fn = nn.SmoothL1Loss()  # Huber loss

        self.replay = ReplayBuffer(self.config.replay_capacity)

        self.step_count = 0
        self.epsilon = self.config.epsilon_start
        self.train_updates = 0

    def set_epsilon_for_difficulty(self, difficulte: str) -> None:
        """Ajuste l'exploration en mode jeu.

        - facile: plus d'exploration (joue plus aléatoire)
        - moyen: mixte
        - difficile: quasi-exploitation
        """
        d = (difficulte or "difficile").lower()
        if d == "facile":
            self.epsilon = 0.40
        elif d == "moyen":
            self.epsilon = 0.15
        else:
            self.epsilon = 0.05

    def _update_epsilon_training(self) -> None:
        # décroissance linéaire
        self.step_count += 1
        frac = min(1.0, self.step_count / float(self.config.epsilon_decay_steps))
        self.epsilon = self.config.epsilon_start + frac * (self.config.epsilon_end - self.config.epsilon_start)

    @torch.no_grad()
    def select_action(self, state: List[float], valid: List[int], training: bool = False) -> int:
        if not valid:
            return -1

        eps = self.epsilon if training else self.epsilon
        if training and random.random() < eps:
            return random.choice(valid)
        if (not training) and random.random() < eps:
            return random.choice(valid)

        x = torch.tensor([state], dtype=torch.float32, device=self.device)
        q_values = self.q(x)[0].detach().cpu().tolist()

        best_a = valid[0]
        best_q = q_values[best_a]
        for a in valid[1:]:
            if q_values[a] > best_q:
                best_q = q_values[a]
                best_a = a
        return best_a

    def remember(self, transition: Transition) -> None:
        self.replay.push(transition)

    def _masked_max(self, q_next: torch.Tensor, next_valid_mask: torch.Tensor) -> torch.Tensor:
        # q_next: [B,9] ; mask: [B,9] in {0,1}
        # invalid -> très négatif
        neg_inf = torch.full_like(q_next, -1e9)
        q_masked = torch.where(next_valid_mask > 0.5, q_next, neg_inf)
        max_q, _ = q_masked.max(dim=1)
        # si aucun coup valide (terminal), max_q sera -1e9 -> on remet à 0
        max_q = torch.where(max_q < -1e8, torch.zeros_like(max_q), max_q)
        return max_q

    def _masked_argmax(self, q_values: torch.Tensor, valid_mask: torch.Tensor) -> torch.Tensor:
        """Argmax par ligne en ignorant les actions invalides.

        Args:
            q_values: [B,9]
            valid_mask: [B,9] in {0,1}

        Returns:
            actions: [B] indices 0..8
        """
        neg_inf = torch.full_like(q_values, -1e9)
        q_masked = torch.where(valid_mask > 0.5, q_values, neg_inf)
        return torch.argmax(q_masked, dim=1)

    def train_step(self) -> Optional[float]:
        if len(self.replay) < self.config.min_replay_size:
            return None

        batch = self.replay.sample(self.config.batch_size)

        states = torch.tensor([t.state for t in batch], dtype=torch.float32, device=self.device)
        actions = torch.tensor([t.action for t in batch], dtype=torch.int64, device=self.device).unsqueeze(1)
        rewards = torch.tensor([t.reward for t in batch], dtype=torch.float32, device=self.device)
        next_states = torch.tensor([t.next_state for t in batch], dtype=torch.float32, device=self.device)
        dones = torch.tensor([t.done for t in batch], dtype=torch.float32, device=self.device)
        next_masks = torch.tensor([t.next_valid_mask for t in batch], dtype=torch.float32, device=self.device)

        q_sa = self.q(states).gather(1, actions).squeeze(1)

        with torch.no_grad():
            # Double DQN:
            # - sélection de l'action avec le réseau online
            # - évaluation avec le target network
            q_next_online = self.q(next_states)
            next_actions = self._masked_argmax(q_next_online, next_masks).unsqueeze(1)  # [B,1]
            q_next_target_all = self.q_target(next_states)
            q_next = q_next_target_all.gather(1, next_actions).squeeze(1)

            # Si aucun coup valide (terminal), q_next sera -1e9 => remettre à 0
            q_next = torch.where(q_next < -1e8, torch.zeros_like(q_next), q_next)
            target = rewards + (1.0 - dones) * self.config.gamma * q_next

        loss = self.loss_fn(q_sa, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Mise à jour périodique du target network
        self.train_updates += 1
        if self.train_updates % self.config.target_update_interval == 0:
            self.q_target.load_state_dict(self.q.state_dict())

        return float(loss.item())

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(
            {
                "model": self.q.state_dict(),
                "target_model": self.q_target.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "step_count": self.step_count,
                "epsilon": self.epsilon,
                "train_updates": self.train_updates,
            },
            path,
        )

    def load(self, path: str) -> bool:
        if not os.path.exists(path):
            return False
        ckpt = torch.load(path, map_location=self.device)
        self.q.load_state_dict(ckpt.get("model", ckpt))
        if "target_model" in ckpt:
            self.q_target.load_state_dict(ckpt["target_model"])
        else:
            self.q_target.load_state_dict(self.q.state_dict())
        if "optimizer" in ckpt:
            try:
                self.optimizer.load_state_dict(ckpt["optimizer"])
            except Exception:
                pass
        self.step_count = int(ckpt.get("step_count", 0))
        self.epsilon = float(ckpt.get("epsilon", self.config.epsilon_end))
        self.train_updates = int(ckpt.get("train_updates", 0))
        return True


def _mask_from_board_abs(board_abs: List[int]) -> List[float]:
    mask = [0.0] * 9
    for idx in valid_actions(board_abs):
        mask[idx] = 1.0
    return mask


def self_play_train(agent: DQNAgent, episodes: int = DEFAULT_SELF_PLAY_EPISODES, verbose_every: int = 500) -> None:
    """Entraîne l'agent par self-play.

    Le même réseau joue les deux camps, mais on encode l'état du point de vue du joueur courant.

    Récompenses (conforme cahier):
    - +1 si le joueur qui vient de jouer gagne
    - -1 attribué au dernier coup de l'adversaire (défaite)
    - 0 en cas de match nul
    """
    agent.q.train()

    for ep in range(1, episodes + 1):
        board_abs = [0] * 9
        player = 1  # 1=X, -1=O

        last_transition = {1: None, -1: None}  # type: ignore[dict-item]
        done = False

        while not done:
            state = [float(v) for v in to_perspective(board_abs, player)]
            valid = valid_actions(board_abs)
            action = agent.select_action(state, valid, training=True)
            if action == -1:
                break

            # jouer
            board_abs[action] = player

            winner = check_winner(board_abs)
            draw = is_draw(board_abs)

            next_state = [float(v) for v in to_perspective(board_abs, -player)]
            next_mask = _mask_from_board_abs(board_abs)

            t = Transition(
                state=state,
                action=action,
                reward=0.0,
                next_state=next_state,
                done=False,
                next_valid_mask=next_mask,
            )
            agent.remember(t)
            last_transition[player] = t

            if winner == player:
                # victoire pour player
                t.reward = 1.0
                t.done = True

                # défaite pour l'adversaire sur son dernier coup
                opp = -player
                if last_transition.get(opp) is not None:
                    last_transition[opp].reward = -1.0
                    last_transition[opp].done = True
                done = True

            elif draw:
                t.reward = 0.0
                t.done = True
                opp = -player
                if last_transition.get(opp) is not None:
                    last_transition[opp].reward = 0.0
                    last_transition[opp].done = True
                done = True

            else:
                player *= -1

            # apprentissage
            agent._update_epsilon_training()
            for _ in range(agent.config.train_steps_per_move):
                agent.train_step()

        if verbose_every and ep % verbose_every == 0:
            # Simple métrique indicative
            pass

    agent.q.eval()
