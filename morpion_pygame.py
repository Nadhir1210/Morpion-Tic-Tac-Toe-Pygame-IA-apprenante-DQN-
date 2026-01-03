"""
Jeu de Morpion (Tic-Tac-Toe) avec Interface Graphique Pygame
Projet Python avec Intelligence Artificielle et interface visuelle
Auteur: Projet pédagogique IA
Date: Décembre 2025
"""

import pygame
import sys
import random
from typing import List, Tuple, Optional

try:
    from dqn_agent import DQNAgent, DQNConfig, self_play_train, DEFAULT_BOOTSTRAP_EPISODES
    from tictactoe_env import from_chars, to_perspective, valid_actions, Transition
    DQN_DISPONIBLE = True
except Exception:
    # Permet au mode "2 Joueurs" de fonctionner même si PyTorch n'est pas installé.
    DQN_DISPONIBLE = False
    DQNAgent = None  # type: ignore[assignment]
    DQNConfig = None  # type: ignore[assignment]
    self_play_train = None  # type: ignore[assignment]
    from_chars = None  # type: ignore[assignment]
    to_perspective = None  # type: ignore[assignment]
    valid_actions = None  # type: ignore[assignment]
    Transition = None  # type: ignore[assignment]
    DEFAULT_BOOTSTRAP_EPISODES = 2500

# Initialisation de Pygame
pygame.init()

# Constantes - Couleurs
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
GRIS = (200, 200, 200)
GRIS_FONCE = (100, 100, 100)
BLEU = (52, 152, 219)
BLEU_FONCE = (41, 128, 185)
ROUGE = (231, 76, 60)
ROUGE_FONCE = (192, 57, 43)
VERT = (46, 204, 113)
VERT_FONCE = (39, 174, 96)
JAUNE = (241, 196, 15)
VIOLET = (155, 89, 182)

# Constantes - Dimensions
LARGEUR_FENETRE = 800
HAUTEUR_FENETRE = 900
TAILLE_GRILLE = 600
MARGE_HAUT = 100
TAILLE_CASE = TAILLE_GRILLE // 3
LARGEUR_LIGNE = 15

# Position de la grille
GRILLE_X = (LARGEUR_FENETRE - TAILLE_GRILLE) // 2
GRILLE_Y = MARGE_HAUT + 50

# Polices
FONT_TITRE = pygame.font.Font(None, 60)
FONT_MENU = pygame.font.Font(None, 40)
FONT_TEXTE = pygame.font.Font(None, 36)
FONT_PETIT = pygame.font.Font(None, 28)


class Morpion:
    """Classe gérant la logique du jeu de Morpion"""
    
    def __init__(self):
        self.plateau = [' ' for _ in range(9)]
        self.joueur_humain = 'X'
        self.joueur_ia = 'O'
        self.joueur_actuel = self.joueur_humain
        self.gagnant = None
        self.combinaison_gagnante = None
    
    def case_disponible(self, position: int) -> bool:
        return self.plateau[position] == ' '
    
    def placer_symbole(self, position: int, symbole: str) -> bool:
        if self.case_disponible(position):
            self.plateau[position] = symbole
            return True
        return False
    
    def verifier_victoire(self, symbole: str) -> Optional[List[int]]:
        """Retourne la combinaison gagnante si victoire, None sinon"""
        combinaisons = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Lignes
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Colonnes
            [0, 4, 8], [2, 4, 6]              # Diagonales
        ]
        
        for combinaison in combinaisons:
            if all(self.plateau[pos] == symbole for pos in combinaison):
                return combinaison
        return None
    
    def verifier_match_nul(self) -> bool:
        return ' ' not in self.plateau
    
    def obtenir_cases_disponibles(self) -> List[int]:
        return [i for i, case in enumerate(self.plateau) if case == ' ']
    
    def reinitialiser(self):
        self.plateau = [' ' for _ in range(9)]
        self.joueur_actuel = self.joueur_humain
        self.gagnant = None
        self.combinaison_gagnante = None


class IntelligenceArtificielle:
    """Compat: ancienne IA Minimax.

    Le projet a été transformé vers du Deep RL (DQN).
    Cette classe est conservée uniquement pour compatibilité de code
    (ne plus utiliser dans la version DQN).
    """

    def __init__(self, symbole_ia: str, symbole_joueur: str):
        self.symbole_ia = symbole_ia
        self.symbole_joueur = symbole_joueur

    def meilleur_coup(self, plateau: List[str], difficulte: str) -> int:
        cases_disponibles = [i for i, c in enumerate(plateau) if c == ' ']
        return random.choice(cases_disponibles) if cases_disponibles else -1


class Bouton:
    """Classe pour créer des boutons interactifs"""
    
    def __init__(self, x: int, y: int, largeur: int, hauteur: int, texte: str,
                 couleur: tuple, couleur_hover: tuple):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_hover = couleur_hover
        self.hover = False
    
    def dessiner(self, ecran: pygame.Surface):
        couleur = self.couleur_hover if self.hover else self.couleur
        pygame.draw.rect(ecran, couleur, self.rect, border_radius=10)
        pygame.draw.rect(ecran, NOIR, self.rect, 3, border_radius=10)
        
        texte_surface = FONT_MENU.render(self.texte, True, BLANC)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        ecran.blit(texte_surface, texte_rect)
    
    def verifier_hover(self, pos: Tuple[int, int]):
        self.hover = self.rect.collidepoint(pos)
    
    def est_clique(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


class JeuPygame:
    """Classe principale gérant le jeu avec Pygame"""
    
    def __init__(self):
        self.ecran = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        pygame.display.set_caption("Morpion - Intelligence Artificielle")
        self.horloge = pygame.time.Clock()
        
        self.jeu = Morpion()
        self.ia = None
        self.agent_dqn: Optional[DQNAgent] = None
        self.modele_path = "models/dqn_tictactoe.pt"
        # Pour un apprentissage correct en jeu IA vs humain:
        # on enregistre (s,a) au tour de l'IA, puis on finalise (s') après le coup humain suivant.
        self._pending_ai_state: Optional[List[float]] = None
        self._pending_ai_action: Optional[int] = None
        self._pending_ai_board_after: Optional[List[int]] = None
        self.difficulte = None
        self.mode_jeu = None
        
        self.etat = "menu"  # menu, difficulte, jeu, fin
        self.message = ""
        self.animation_victoire = 0
        
        self.creer_boutons()
    
    def creer_boutons(self):
        """Crée tous les boutons du jeu"""
        # Boutons du menu principal
        self.boutons_menu = [
            Bouton(250, 250, 300, 70, "Jouer vs IA", BLEU, BLEU_FONCE),
            Bouton(250, 340, 300, 70, "2 Joueurs", VERT, VERT_FONCE),
            Bouton(250, 430, 300, 70, "IA vs IA", VIOLET, (128, 58, 150)),
            Bouton(250, 520, 300, 70, "Quitter", ROUGE, ROUGE_FONCE)
        ]
        
        # Boutons de difficulté
        self.boutons_difficulte = [
            Bouton(250, 250, 300, 70, "Facile", VERT, VERT_FONCE),
            Bouton(250, 340, 300, 70, "Moyen", JAUNE, (243, 156, 18)),
            Bouton(250, 430, 300, 70, "Difficile", ROUGE, ROUGE_FONCE),
            Bouton(250, 520, 300, 70, "Retour", GRIS_FONCE, NOIR)
        ]
        
        # Boutons de fin de partie
        self.boutons_fin = [
            Bouton(250, 650, 300, 60, "Rejouer", VERT, VERT_FONCE),
            Bouton(250, 730, 300, 60, "Menu", BLEU, BLEU_FONCE)
        ]
    
    def dessiner_grille(self):
        """Dessine la grille de jeu"""
        # Fond de la grille
        pygame.draw.rect(self.ecran, BLANC, 
                        (GRILLE_X, GRILLE_Y, TAILLE_GRILLE, TAILLE_GRILLE))
        
        # Lignes verticales
        for i in range(1, 3):
            x = GRILLE_X + i * TAILLE_CASE
            pygame.draw.line(self.ecran, NOIR,
                           (x, GRILLE_Y),
                           (x, GRILLE_Y + TAILLE_GRILLE),
                           LARGEUR_LIGNE)
        
        # Lignes horizontales
        for i in range(1, 3):
            y = GRILLE_Y + i * TAILLE_CASE
            pygame.draw.line(self.ecran, NOIR,
                           (GRILLE_X, y),
                           (GRILLE_X + TAILLE_GRILLE, y),
                           LARGEUR_LIGNE)
    
    def dessiner_symboles(self):
        """Dessine les X et O sur la grille"""
        for i, symbole in enumerate(self.jeu.plateau):
            if symbole != ' ':
                ligne = i // 3
                colonne = i % 3
                
                centre_x = GRILLE_X + colonne * TAILLE_CASE + TAILLE_CASE // 2
                centre_y = GRILLE_Y + ligne * TAILLE_CASE + TAILLE_CASE // 2
                
                if symbole == 'X':
                    self.dessiner_x(centre_x, centre_y)
                else:
                    self.dessiner_o(centre_x, centre_y)
    
    def dessiner_x(self, x: int, y: int):
        """Dessine un X"""
        taille = TAILLE_CASE // 3
        couleur = BLEU
        epaisseur = 12
        
        pygame.draw.line(self.ecran, couleur,
                        (x - taille, y - taille),
                        (x + taille, y + taille),
                        epaisseur)
        pygame.draw.line(self.ecran, couleur,
                        (x + taille, y - taille),
                        (x - taille, y + taille),
                        epaisseur)
    
    def dessiner_o(self, x: int, y: int):
        """Dessine un O"""
        rayon = TAILLE_CASE // 3
        couleur = ROUGE
        epaisseur = 12
        
        pygame.draw.circle(self.ecran, couleur, (x, y), rayon, epaisseur)
    
    def dessiner_ligne_victoire(self):
        """Dessine une ligne animée sur la combinaison gagnante"""
        if self.jeu.combinaison_gagnante:
            # Animation de pulsation
            self.animation_victoire += 0.1
            epaisseur = int(10 + 5 * abs(pygame.math.Vector2(1, 0).rotate(self.animation_victoire * 180).x))
            
            # Calculer les positions de début et fin
            debut = self.jeu.combinaison_gagnante[0]
            fin = self.jeu.combinaison_gagnante[2]
            
            debut_ligne = debut // 3
            debut_colonne = debut % 3
            fin_ligne = fin // 3
            fin_colonne = fin % 3
            
            debut_x = GRILLE_X + debut_colonne * TAILLE_CASE + TAILLE_CASE // 2
            debut_y = GRILLE_Y + debut_ligne * TAILLE_CASE + TAILLE_CASE // 2
            fin_x = GRILLE_X + fin_colonne * TAILLE_CASE + TAILLE_CASE // 2
            fin_y = GRILLE_Y + fin_ligne * TAILLE_CASE + TAILLE_CASE // 2
            
            # Dessiner la ligne
            pygame.draw.line(self.ecran, JAUNE,
                           (debut_x, debut_y),
                           (fin_x, fin_y),
                           epaisseur)
    
    def obtenir_case_cliquee(self, pos: Tuple[int, int]) -> Optional[int]:
        """Retourne l'indice de la case cliquée, ou None"""
        x, y = pos
        
        if (GRILLE_X <= x <= GRILLE_X + TAILLE_GRILLE and
            GRILLE_Y <= y <= GRILLE_Y + TAILLE_GRILLE):
            
            colonne = (x - GRILLE_X) // TAILLE_CASE
            ligne = (y - GRILLE_Y) // TAILLE_CASE
            
            return ligne * 3 + colonne
        
        return None
    
    def dessiner_menu_principal(self):
        """Dessine le menu principal"""
        self.ecran.fill(GRIS)
        
        # Titre
        titre = FONT_TITRE.render("MORPION", True, NOIR)
        titre_rect = titre.get_rect(center=(LARGEUR_FENETRE // 2, 120))
        self.ecran.blit(titre, titre_rect)
        
        sous_titre = FONT_PETIT.render("avec Intelligence Artificielle", True, GRIS_FONCE)
        sous_titre_rect = sous_titre.get_rect(center=(LARGEUR_FENETRE // 2, 170))
        self.ecran.blit(sous_titre, sous_titre_rect)
        
        # Dessiner les boutons
        for bouton in self.boutons_menu:
            bouton.dessiner(self.ecran)
    
    def dessiner_menu_difficulte(self):
        """Dessine le menu de sélection de difficulté"""
        self.ecran.fill(GRIS)
        
        titre = FONT_TITRE.render("DIFFICULTÉ", True, NOIR)
        titre_rect = titre.get_rect(center=(LARGEUR_FENETRE // 2, 120))
        self.ecran.blit(titre, titre_rect)
        
        for bouton in self.boutons_difficulte:
            bouton.dessiner(self.ecran)
    
    def dessiner_jeu(self):
        """Dessine l'écran de jeu"""
        self.ecran.fill(GRIS)
        
        # Message en haut
        if self.message:
            texte = FONT_TEXTE.render(self.message, True, NOIR)
            texte_rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, 50))
            self.ecran.blit(texte, texte_rect)
        
        # Grille et symboles
        self.dessiner_grille()
        self.dessiner_symboles()
        
        # Ligne de victoire si applicable
        if self.jeu.gagnant:
            self.dessiner_ligne_victoire()
    
    def dessiner_fin(self):
        """Dessine l'écran de fin de partie"""
        self.dessiner_jeu()
        
        # Panneau semi-transparent
        overlay = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        overlay.set_alpha(200)
        overlay.fill(BLANC)
        self.ecran.blit(overlay, (0, 0))
        
        # Message de résultat
        if self.jeu.gagnant == 'X':
            if self.mode_jeu == "ia":
                texte_principal = "🎉 VOUS AVEZ GAGNÉ ! 🎉"
                couleur = VERT
            else:
                texte_principal = "🏆 JOUEUR X GAGNE ! 🏆"
                couleur = BLEU
        elif self.jeu.gagnant == 'O':
            if self.mode_jeu == "ia":
                texte_principal = "🤖 L'IA A GAGNÉ !"
                couleur = ROUGE
            else:
                texte_principal = "🏆 JOUEUR O GAGNE ! 🏆"
                couleur = ROUGE
        else:
            texte_principal = "⚖️  MATCH NUL !"
            couleur = JAUNE
        
        texte = FONT_TITRE.render(texte_principal, True, couleur)
        texte_rect = texte.get_rect(center=(LARGEUR_FENETRE // 2, 300))
        self.ecran.blit(texte, texte_rect)
        
        # Boutons
        for bouton in self.boutons_fin:
            bouton.dessiner(self.ecran)
    
    def gerer_clic_menu(self, pos: Tuple[int, int]):
        """Gère les clics dans le menu principal"""
        if self.boutons_menu[0].est_clique(pos):  # Jouer vs IA
            self.etat = "difficulte"
            self.mode_jeu = "ia"
        elif self.boutons_menu[1].est_clique(pos):  # 2 Joueurs
            self.mode_jeu = "2joueurs"
            self.demarrer_partie()
        elif self.boutons_menu[2].est_clique(pos):  # IA vs IA
            self.mode_jeu = "ia_vs_ia"
            self.difficulte = "difficile"
            self.demarrer_partie()
        elif self.boutons_menu[3].est_clique(pos):  # Quitter
            pygame.quit()
            sys.exit()
    
    def gerer_clic_difficulte(self, pos: Tuple[int, int]):
        """Gère les clics dans le menu de difficulté"""
        if self.boutons_difficulte[0].est_clique(pos):  # Facile
            self.difficulte = "facile"
            self.demarrer_partie()
        elif self.boutons_difficulte[1].est_clique(pos):  # Moyen
            self.difficulte = "moyen"
            self.demarrer_partie()
        elif self.boutons_difficulte[2].est_clique(pos):  # Difficile
            self.difficulte = "difficile"
            self.demarrer_partie()
        elif self.boutons_difficulte[3].est_clique(pos):  # Retour
            self.etat = "menu"
    
    def gerer_clic_jeu(self, pos: Tuple[int, int]):
        """Gère les clics pendant le jeu"""
        if self.jeu.gagnant or self.jeu.verifier_match_nul():
            return
        
        case = self.obtenir_case_cliquee(pos)
        
        if case is not None and self.jeu.case_disponible(case):
            if self.mode_jeu == "ia":
                # Tour du joueur
                self.jeu.placer_symbole(case, self.jeu.joueur_humain)

                # Finaliser la transition de l'IA précédente (si elle existe)
                # s' = état après la réponse humaine.
                if self.agent_dqn and self._pending_ai_state is not None and self._pending_ai_action is not None:
                    board_after_human_abs, agent_player = from_chars(self.jeu.plateau, self.jeu.joueur_ia)
                    next_state = [float(v) for v in to_perspective(board_after_human_abs, agent_player)]
                    next_mask = [1.0 if i in valid_actions(board_after_human_abs) else 0.0 for i in range(9)]

                    human_wins = self.jeu.verifier_victoire(self.jeu.joueur_humain) is not None
                    draw = self.jeu.verifier_match_nul()
                    reward = -1.0 if human_wins else 0.0
                    done = human_wins or draw

                    t = Transition(
                        state=self._pending_ai_state,
                        action=self._pending_ai_action,
                        reward=reward,
                        next_state=next_state,
                        done=done,
                        next_valid_mask=next_mask,
                    )
                    self.agent_dqn.remember(t)
                    for _ in range(self.agent_dqn.config.train_steps_per_move):
                        self.agent_dqn.train_step()
                    if done:
                        self.agent_dqn.save(self.modele_path)

                    self._pending_ai_state = None
                    self._pending_ai_action = None
                    self._pending_ai_board_after = None

                self.verifier_etat_jeu()
                
                # Tour de l'IA si le jeu continue
                if not self.jeu.gagnant and not self.jeu.verifier_match_nul():
                    pygame.time.wait(300)
                    self.tour_ia()
            
            elif self.mode_jeu == "2joueurs":
                # Alternance entre X et O
                self.jeu.placer_symbole(case, self.jeu.joueur_actuel)
                self.verifier_etat_jeu()
                
                if not self.jeu.gagnant and not self.jeu.verifier_match_nul():
                    self.jeu.joueur_actuel = 'O' if self.jeu.joueur_actuel == 'X' else 'X'
                    self.message = f"Tour du joueur {self.jeu.joueur_actuel}"
    
    def gerer_clic_fin(self, pos: Tuple[int, int]):
        """Gère les clics dans l'écran de fin"""
        if self.boutons_fin[0].est_clique(pos):  # Rejouer
            if self.mode_jeu == "ia":
                self.etat = "difficulte"
            else:
                self.demarrer_partie()
        elif self.boutons_fin[1].est_clique(pos):  # Menu
            self.etat = "menu"
    
    def demarrer_partie(self):
        """Démarre une nouvelle partie"""
        self.jeu.reinitialiser()
        self.etat = "jeu"
        self.animation_victoire = 0
        
        if self.mode_jeu == "ia":
            if not DQN_DISPONIBLE:
                self.message = "Mode IA indisponible: installez PyTorch (torch)."
                pygame.time.wait(1200)
                self.etat = "menu"
                return

            # DQN: initialise/charge le modèle et ajuste epsilon selon difficulté.
            if self.agent_dqn is None:
                self.agent_dqn = DQNAgent(DQNConfig())
                charge = self.agent_dqn.load(self.modele_path)
                if not charge:
                    # Petit entraînement initial self-play (rapide) pour éviter un agent totalement aléatoire.
                    # Les données sont générées par le jeu (pas de dataset externe).
                    self.message = "Entraînement initial de l'IA (DQN)..."
                    pygame.display.flip()
                    pygame.event.pump()
                    self_play_train(self.agent_dqn, episodes=DEFAULT_BOOTSTRAP_EPISODES, verbose_every=0)
                    self.agent_dqn.save(self.modele_path)

            self.agent_dqn.set_epsilon_for_difficulty(self.difficulte)
            self._pending_ai_state = None
            self._pending_ai_action = None
            self._pending_ai_board_after = None
            self.message = f"Votre tour ! (Niveau: {self.difficulte.capitalize()})"
        elif self.mode_jeu == "2joueurs":
            self.message = "Tour du joueur X"
        elif self.mode_jeu == "ia_vs_ia":
            if not DQN_DISPONIBLE:
                self.message = "Mode IA indisponible: installez PyTorch (torch)."
                pygame.time.wait(1200)
                self.etat = "menu"
                return

            if self.agent_dqn is None:
                self.agent_dqn = DQNAgent(DQNConfig())
                charge = self.agent_dqn.load(self.modele_path)
                if not charge:
                    self.message = "Entraînement initial de l'IA (DQN)..."
                    pygame.display.flip()
                    pygame.event.pump()
                    self_play_train(self.agent_dqn, episodes=DEFAULT_BOOTSTRAP_EPISODES, verbose_every=0)
                    self.agent_dqn.save(self.modele_path)

            # IA vs IA: démonstration (peut aussi continuer à apprendre en ligne)
            self._pending_ai_state = None
            self._pending_ai_action = None
            self._pending_ai_board_after = None
            self.message = "IA vs IA - Démonstration"
            # Démarrer la démonstration après un court délai
            pygame.time.set_timer(pygame.USEREVENT + 1, 1000)
    
    def tour_ia(self):
        """Exécute le tour de l'IA"""
        if not self.agent_dqn:
            return

        board_abs, agent_player = from_chars(self.jeu.plateau, self.jeu.joueur_ia)
        # Agent joue O => agent_player = -1, état depuis sa perspective
        state = [float(v) for v in to_perspective(board_abs, agent_player)]
        valid = valid_actions(board_abs)

        action = self.agent_dqn.select_action(state, valid, training=False)
        if action == -1:
            return

        # Appliquer le coup
        self.jeu.placer_symbole(action, self.jeu.joueur_ia)

        # Si l'IA gagne ou match nul immédiatement, transition terminale.
        ai_wins = self.jeu.verifier_victoire(self.jeu.joueur_ia) is not None
        draw = self.jeu.verifier_match_nul()

        if ai_wins or draw:
            board_after_abs, _ = from_chars(self.jeu.plateau, self.jeu.joueur_ia)
            next_state = [float(v) for v in to_perspective(board_after_abs, agent_player)]
            next_mask = [0.0] * 9
            reward = 1.0 if ai_wins else 0.0
            t = Transition(
                state=state,
                action=action,
                reward=reward,
                next_state=next_state,
                done=True,
                next_valid_mask=next_mask,
            )
            self.agent_dqn.remember(t)
            for _ in range(self.agent_dqn.config.train_steps_per_move):
                self.agent_dqn.train_step()
            self.agent_dqn.save(self.modele_path)
            self._pending_ai_state = None
            self._pending_ai_action = None
            self._pending_ai_board_after = None
        else:
            # Sinon, on attend le coup humain pour produire s'
            board_after_abs, _ = from_chars(self.jeu.plateau, self.jeu.joueur_ia)
            self._pending_ai_state = state
            self._pending_ai_action = action
            self._pending_ai_board_after = board_after_abs

        self.verifier_etat_jeu()
    
    def tour_ia_vs_ia(self):
        """Exécute un tour dans le mode IA vs IA"""
        if self.jeu.gagnant or self.jeu.verifier_match_nul():
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Arrêter le timer
            return

        if not self.agent_dqn:
            return

        joueur = self.jeu.joueur_actuel  # 'X' ou 'O'
        board_abs, agent_player = from_chars(self.jeu.plateau, joueur)
        state = [float(v) for v in to_perspective(board_abs, agent_player)]
        valid = valid_actions(board_abs)
        action = self.agent_dqn.select_action(state, valid, training=False)
        if action == -1:
            return

        self.jeu.placer_symbole(action, joueur)
        self.verifier_etat_jeu()
        self.jeu.joueur_actuel = 'O' if joueur == 'X' else 'X'
    
    def verifier_etat_jeu(self):
        """Vérifie l'état du jeu et met à jour si nécessaire"""
        combinaison_x = self.jeu.verifier_victoire('X')
        combinaison_o = self.jeu.verifier_victoire('O')
        
        if combinaison_x:
            self.jeu.gagnant = 'X'
            self.jeu.combinaison_gagnante = combinaison_x
            pygame.time.wait(1000)
            self.etat = "fin"
        elif combinaison_o:
            self.jeu.gagnant = 'O'
            self.jeu.combinaison_gagnante = combinaison_o
            pygame.time.wait(1000)
            self.etat = "fin"
        elif self.jeu.verifier_match_nul():
            self.jeu.gagnant = 'nul'
            pygame.time.wait(1000)
            self.etat = "fin"
    
    def lancer(self):
        """Boucle principale du jeu"""
        en_cours = True
        
        while en_cours:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    en_cours = False
                
                elif event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    if self.etat == "menu":
                        for bouton in self.boutons_menu:
                            bouton.verifier_hover(pos)
                    elif self.etat == "difficulte":
                        for bouton in self.boutons_difficulte:
                            bouton.verifier_hover(pos)
                    elif self.etat == "fin":
                        for bouton in self.boutons_fin:
                            bouton.verifier_hover(pos)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.etat == "menu":
                        self.gerer_clic_menu(pos)
                    elif self.etat == "difficulte":
                        self.gerer_clic_difficulte(pos)
                    elif self.etat == "jeu":
                        self.gerer_clic_jeu(pos)
                    elif self.etat == "fin":
                        self.gerer_clic_fin(pos)
                
                elif event.type == pygame.USEREVENT + 1:  # Timer pour IA vs IA
                    if self.mode_jeu == "ia_vs_ia" and self.etat == "jeu":
                        self.tour_ia_vs_ia()
            
            # Dessiner selon l'état
            if self.etat == "menu":
                self.dessiner_menu_principal()
            elif self.etat == "difficulte":
                self.dessiner_menu_difficulte()
            elif self.etat == "jeu":
                self.dessiner_jeu()
            elif self.etat == "fin":
                self.dessiner_fin()
            
            pygame.display.flip()
            self.horloge.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Fonction principale"""
    jeu = JeuPygame()
    jeu.lancer()


if __name__ == "__main__":
    main()
