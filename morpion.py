"""
Jeu de Morpion (Tic-Tac-Toe) avec Intelligence Artificielle
Projet Python utilisant l'algorithme Minimax
Auteur: Projet pédagogique IA
Date: Décembre 2025
"""

import random
import copy
from typing import List, Tuple, Optional


class Morpion:
    """Classe principale gérant le plateau de jeu et les règles du Morpion"""
    
    def __init__(self):
        """Initialise un nouveau plateau de jeu vide"""
        self.plateau = [' ' for _ in range(9)]  # Plateau 3x3 représenté en liste de 9 cases
        self.joueur_humain = 'X'
        self.joueur_ia = 'O'
        self.joueur_actuel = self.joueur_humain
    
    def afficher_plateau(self):
        """Affiche le plateau de jeu dans la console de manière claire et lisible"""
        print("\n")
        for i in range(0, 9, 3):
            ligne = []
            for j in range(3):
                case = self.plateau[i + j]
                # Affiche le numéro de case si vide, sinon le symbole
                affichage = str(i + j + 1) if case == ' ' else case
                ligne.append(f" {affichage} ")
            print("|".join(ligne))
            if i < 6:
                print("---+---+---")
        print("\n")
    
    def case_disponible(self, position: int) -> bool:
        """
        Vérifie si une case est disponible
        
        Args:
            position: Numéro de la case (0-8)
            
        Returns:
            True si la case est vide, False sinon
        """
        return self.plateau[position] == ' '
    
    def placer_symbole(self, position: int, symbole: str) -> bool:
        """
        Place un symbole sur le plateau
        
        Args:
            position: Numéro de la case (0-8)
            symbole: 'X' ou 'O'
            
        Returns:
            True si le placement a réussi, False sinon
        """
        if self.case_disponible(position):
            self.plateau[position] = symbole
            return True
        return False
    
    def verifier_victoire(self, symbole: str) -> bool:
        """
        Vérifie si un joueur a gagné
        
        Args:
            symbole: 'X' ou 'O'
            
        Returns:
            True si le joueur a aligné 3 symboles, False sinon
        """
        # Définition de toutes les combinaisons gagnantes possibles
        combinaisons_gagnantes = [
            [0, 1, 2],  # Ligne 1
            [3, 4, 5],  # Ligne 2
            [6, 7, 8],  # Ligne 3
            [0, 3, 6],  # Colonne 1
            [1, 4, 7],  # Colonne 2
            [2, 5, 8],  # Colonne 3
            [0, 4, 8],  # Diagonale \
            [2, 4, 6]   # Diagonale /
        ]
        
        for combinaison in combinaisons_gagnantes:
            if all(self.plateau[pos] == symbole for pos in combinaison):
                return True
        return False
    
    def verifier_match_nul(self) -> bool:
        """
        Vérifie si la partie est un match nul (plateau rempli sans gagnant)
        
        Returns:
            True si match nul, False sinon
        """
        return ' ' not in self.plateau
    
    def obtenir_cases_disponibles(self) -> List[int]:
        """
        Retourne la liste des positions disponibles sur le plateau
        
        Returns:
            Liste des indices des cases vides
        """
        return [i for i, case in enumerate(self.plateau) if case == ' ']
    
    def reinitialiser(self):
        """Réinitialise le plateau pour une nouvelle partie"""
        self.plateau = [' ' for _ in range(9)]
        self.joueur_actuel = self.joueur_humain


class IntelligenceArtificielle:
    """Classe gérant l'intelligence artificielle avec l'algorithme Minimax"""
    
    def __init__(self, symbole_ia: str, symbole_joueur: str):
        """
        Initialise l'IA
        
        Args:
            symbole_ia: Symbole de l'IA ('X' ou 'O')
            symbole_joueur: Symbole du joueur humain
        """
        self.symbole_ia = symbole_ia
        self.symbole_joueur = symbole_joueur
    
    def minimax(self, plateau: List[str], profondeur: int, est_maximisant: bool, 
                alpha: float = float('-inf'), beta: float = float('inf')) -> int:
        """
        Algorithme Minimax avec élagage Alpha-Beta pour déterminer le meilleur coup
        
        Args:
            plateau: État actuel du plateau
            profondeur: Profondeur actuelle dans l'arbre de décision
            est_maximisant: True si c'est le tour de l'IA, False sinon
            alpha: Valeur alpha pour l'élagage
            beta: Valeur beta pour l'élagage
            
        Returns:
            Score du coup (-1, 0, ou 1)
        """
        # Créer un objet temporaire pour vérifier l'état du jeu
        jeu_temp = Morpion()
        jeu_temp.plateau = plateau.copy()
        
        # Conditions terminales
        if jeu_temp.verifier_victoire(self.symbole_ia):
            return 10 - profondeur  # Favorise les victoires rapides
        elif jeu_temp.verifier_victoire(self.symbole_joueur):
            return profondeur - 10  # Pénalise les défaites
        elif jeu_temp.verifier_match_nul():
            return 0
        
        if est_maximisant:
            # Tour de l'IA - cherche à maximiser le score
            meilleur_score = float('-inf')
            for position in jeu_temp.obtenir_cases_disponibles():
                plateau[position] = self.symbole_ia
                score = self.minimax(plateau, profondeur + 1, False, alpha, beta)
                plateau[position] = ' '
                meilleur_score = max(score, meilleur_score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Élagage Beta
            return meilleur_score
        else:
            # Tour du joueur - cherche à minimiser le score
            meilleur_score = float('inf')
            for position in jeu_temp.obtenir_cases_disponibles():
                plateau[position] = self.symbole_joueur
                score = self.minimax(plateau, profondeur + 1, True, alpha, beta)
                plateau[position] = ' '
                meilleur_score = min(score, meilleur_score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Élagage Alpha
            return meilleur_score
    
    def meilleur_coup(self, plateau: List[str], difficulte: str) -> int:
        """
        Détermine le meilleur coup selon le niveau de difficulté
        
        Args:
            plateau: État actuel du plateau
            difficulte: 'facile', 'moyen', ou 'difficile'
            
        Returns:
            Position du meilleur coup (0-8)
        """
        jeu_temp = Morpion()
        jeu_temp.plateau = plateau.copy()
        cases_disponibles = jeu_temp.obtenir_cases_disponibles()
        
        if not cases_disponibles:
            return -1
        
        if difficulte == 'facile':
            # Mode facile : coups aléatoires
            return random.choice(cases_disponibles)
        
        elif difficulte == 'moyen':
            # Mode moyen : 50% Minimax, 50% aléatoire
            if random.random() < 0.5:
                return random.choice(cases_disponibles)
            # Sinon, utilise Minimax avec profondeur limitée
        
        # Mode difficile ou moyen (partie Minimax) : utilise l'algorithme complet
        meilleur_score = float('-inf')
        meilleur_position = cases_disponibles[0]
        
        for position in cases_disponibles:
            plateau_copie = plateau.copy()
            plateau_copie[position] = self.symbole_ia
            score = self.minimax(plateau_copie, 0, False)
            
            if score > meilleur_score:
                meilleur_score = score
                meilleur_position = position
        
        return meilleur_position


class JeuMorpion:
    """Classe principale gérant le déroulement du jeu"""
    
    def __init__(self):
        """Initialise le jeu"""
        self.jeu = Morpion()
        self.ia = None
        self.mode_jeu = None
        self.difficulte = None
    
    def afficher_menu_principal(self):
        """Affiche le menu principal du jeu"""
        print("\n" + "="*50)
        print("   MORPION (TIC-TAC-TOE) AVEC INTELLIGENCE ARTIFICIELLE")
        print("="*50)
        print("\n1. Jouer contre l'IA")
        print("2. Jouer contre un autre joueur")
        print("3. IA contre IA (démonstration)")
        print("4. Règles du jeu")
        print("5. Quitter")
        print("\n" + "="*50)
    
    def afficher_regles(self):
        """Affiche les règles du jeu"""
        print("\n" + "="*50)
        print("   RÈGLES DU MORPION")
        print("="*50)
        print("\n• Le jeu se joue sur une grille de 3x3 cases")
        print("• Deux joueurs placent leurs symboles (X et O) à tour de rôle")
        print("• Le premier qui aligne 3 symboles identiques gagne")
        print("  (horizontalement, verticalement ou en diagonale)")
        print("• Si toutes les cases sont remplies sans gagnant : match nul")
        print("\n• Pour jouer, entrez le numéro de la case (1-9)")
        print("="*50)
        input("\nAppuyez sur Entrée pour continuer...")
    
    def choisir_difficulte(self) -> str:
        """
        Permet au joueur de choisir le niveau de difficulté
        
        Returns:
            Niveau de difficulté choisi
        """
        print("\n" + "="*50)
        print("   NIVEAU DE DIFFICULTÉ")
        print("="*50)
        print("\n1. Facile (coups aléatoires)")
        print("2. Moyen (IA partiellement stratégique)")
        print("3. Difficile (IA imbattable)")
        print("\n" + "="*50)
        
        while True:
            choix = input("\nChoisissez le niveau (1-3) : ").strip()
            if choix == '1':
                return 'facile'
            elif choix == '2':
                return 'moyen'
            elif choix == '3':
                return 'difficile'
            else:
                print("❌ Choix invalide. Veuillez entrer 1, 2 ou 3.")
    
    def tour_joueur_humain(self, symbole: str) -> bool:
        """
        Gère le tour d'un joueur humain
        
        Args:
            symbole: Symbole du joueur ('X' ou 'O')
            
        Returns:
            True si le coup a été joué, False si abandon
        """
        while True:
            try:
                print(f"\n🎮 Tour du joueur {symbole}")
                choix = input("Choisissez une case (1-9) ou 'q' pour quitter : ").strip().lower()
                
                if choix == 'q':
                    return False
                
                position = int(choix) - 1
                
                if position < 0 or position > 8:
                    print("❌ Numéro de case invalide. Choisissez entre 1 et 9.")
                    continue
                
                if self.jeu.placer_symbole(position, symbole):
                    return True
                else:
                    print("❌ Cette case est déjà occupée. Choisissez une autre case.")
            
            except ValueError:
                print("❌ Entrée invalide. Veuillez entrer un nombre entre 1 et 9.")
            except Exception as e:
                print(f"❌ Erreur : {e}")
    
    def tour_ia(self, symbole: str, difficulte: str):
        """
        Gère le tour de l'IA
        
        Args:
            symbole: Symbole de l'IA
            difficulte: Niveau de difficulté
        """
        print(f"\n🤖 L'IA ({symbole}) réfléchit...")
        position = self.ia.meilleur_coup(self.jeu.plateau, difficulte)
        self.jeu.placer_symbole(position, symbole)
        print(f"🤖 L'IA joue la case {position + 1}")
    
    def verifier_fin_partie(self) -> Optional[str]:
        """
        Vérifie si la partie est terminée
        
        Returns:
            'X' si X gagne, 'O' si O gagne, 'nul' si match nul, None si partie en cours
        """
        if self.jeu.verifier_victoire('X'):
            return 'X'
        elif self.jeu.verifier_victoire('O'):
            return 'O'
        elif self.jeu.verifier_match_nul():
            return 'nul'
        return None
    
    def jouer_partie_contre_ia(self):
        """Lance une partie contre l'IA"""
        self.difficulte = self.choisir_difficulte()
        self.jeu.reinitialiser()
        self.ia = IntelligenceArtificielle(self.jeu.joueur_ia, self.jeu.joueur_humain)
        
        print(f"\n🎮 Partie lancée en mode {self.difficulte.upper()}")
        print(f"Vous êtes {self.jeu.joueur_humain} et l'IA est {self.jeu.joueur_ia}")
        
        while True:
            self.jeu.afficher_plateau()
            
            # Tour du joueur humain
            if not self.tour_joueur_humain(self.jeu.joueur_humain):
                print("\n👋 Partie abandonnée.")
                return
            
            # Vérifier si le joueur a gagné
            resultat = self.verifier_fin_partie()
            if resultat:
                self.jeu.afficher_plateau()
                self.afficher_resultat(resultat)
                return
            
            # Tour de l'IA
            self.tour_ia(self.jeu.joueur_ia, self.difficulte)
            
            # Vérifier si l'IA a gagné
            resultat = self.verifier_fin_partie()
            if resultat:
                self.jeu.afficher_plateau()
                self.afficher_resultat(resultat)
                return
    
    def jouer_partie_deux_joueurs(self):
        """Lance une partie entre deux joueurs humains"""
        self.jeu.reinitialiser()
        
        print("\n🎮 Mode deux joueurs")
        print(f"Joueur 1 : X")
        print(f"Joueur 2 : O")
        
        symboles = ['X', 'O']
        joueur_actuel = 0
        
        while True:
            self.jeu.afficher_plateau()
            
            # Tour du joueur actuel
            if not self.tour_joueur_humain(symboles[joueur_actuel]):
                print("\n👋 Partie abandonnée.")
                return
            
            # Vérifier si le joueur a gagné
            resultat = self.verifier_fin_partie()
            if resultat:
                self.jeu.afficher_plateau()
                self.afficher_resultat(resultat)
                return
            
            # Changer de joueur
            joueur_actuel = 1 - joueur_actuel
    
    def jouer_partie_ia_vs_ia(self):
        """Lance une démonstration IA contre IA"""
        self.jeu.reinitialiser()
        ia1 = IntelligenceArtificielle('X', 'O')
        ia2 = IntelligenceArtificielle('O', 'X')
        
        print("\n🤖 Démonstration : IA contre IA")
        print("IA 1 (X) vs IA 2 (O)")
        input("\nAppuyez sur Entrée pour commencer...")
        
        symboles = ['X', 'O']
        ias = [ia1, ia2]
        tour = 0
        
        while True:
            self.jeu.afficher_plateau()
            
            symbole_actuel = symboles[tour]
            ia_actuelle = ias[tour]
            
            print(f"\n🤖 IA {tour + 1} ({symbole_actuel}) réfléchit...")
            input("Appuyez sur Entrée pour voir le coup...")
            
            position = ia_actuelle.meilleur_coup(self.jeu.plateau, 'difficile')
            self.jeu.placer_symbole(position, symbole_actuel)
            print(f"🤖 IA {tour + 1} joue la case {position + 1}")
            
            # Vérifier la fin de partie
            resultat = self.verifier_fin_partie()
            if resultat:
                self.jeu.afficher_plateau()
                self.afficher_resultat(resultat)
                return
            
            # Changer de tour
            tour = 1 - tour
    
    def afficher_resultat(self, resultat: str):
        """
        Affiche le résultat de la partie
        
        Args:
            resultat: 'X', 'O', ou 'nul'
        """
        print("\n" + "="*50)
        if resultat == 'nul':
            print("   ⚖️  MATCH NUL !")
        elif resultat == self.jeu.joueur_humain and self.mode_jeu == 1:
            print("   🎉 FÉLICITATIONS ! VOUS AVEZ GAGNÉ !")
        elif resultat == self.jeu.joueur_ia and self.mode_jeu == 1:
            print("   😔 L'IA A GAGNÉ ! RÉESSAYEZ !")
        else:
            print(f"   🏆 LE JOUEUR {resultat} A GAGNÉ !")
        print("="*50)
    
    def demander_rejouer(self) -> bool:
        """
        Demande au joueur s'il veut rejouer
        
        Returns:
            True si le joueur veut rejouer, False sinon
        """
        while True:
            choix = input("\n🔄 Voulez-vous rejouer ? (o/n) : ").strip().lower()
            if choix in ['o', 'oui', 'y', 'yes']:
                return True
            elif choix in ['n', 'non', 'no']:
                return False
            else:
                print("❌ Réponse invalide. Veuillez répondre par 'o' ou 'n'.")
    
    def lancer(self):
        """Lance le jeu et gère la boucle principale"""
        while True:
            self.afficher_menu_principal()
            
            try:
                choix = input("\nVotre choix (1-5) : ").strip()
                
                if choix == '1':
                    self.mode_jeu = 1
                    self.jouer_partie_contre_ia()
                    if not self.demander_rejouer():
                        break
                
                elif choix == '2':
                    self.mode_jeu = 2
                    self.jouer_partie_deux_joueurs()
                    if not self.demander_rejouer():
                        break
                
                elif choix == '3':
                    self.mode_jeu = 3
                    self.jouer_partie_ia_vs_ia()
                    if not self.demander_rejouer():
                        break
                
                elif choix == '4':
                    self.afficher_regles()
                
                elif choix == '5':
                    print("\n👋 Merci d'avoir joué ! À bientôt !")
                    break
                
                else:
                    print("❌ Choix invalide. Veuillez entrer un nombre entre 1 et 5.")
            
            except KeyboardInterrupt:
                print("\n\n👋 Programme interrompu. Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur inattendue : {e}")


def main():
    """Fonction principale du programme"""
    jeu = JeuMorpion()
    jeu.lancer()


if __name__ == "__main__":
    main()
