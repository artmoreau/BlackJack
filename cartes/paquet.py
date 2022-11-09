import random
from cartes.carte import Carte


class Paquet:

    def __init__(self, nbr_paquet=1):
        self.cartes = []
        for i in range(nbr_paquet):
            for couleur in range(4):
                for valeur in range(1, 14):
                    carte = Carte(couleur, valeur)
                    self.cartes.append(carte)

    def __str__(self):

        res_nbr_carte = f"{len(self.cartes)} cartes:\n"
        res_cartes = []
        for carte in self.cartes:
            res_cartes.append(str(carte))
        return res_nbr_carte + '\n'.join(res_cartes)

    def shuffle(self):
        """ mélange le paquet courant """
        random.shuffle(self.cartes)

    def pop_carte(self):
        """ enlève la première carte du paquet courant et la retourne """
        return self.cartes.pop()

    def ajouter_carte(self, carte):
        """ ajoute la crate carte au paquet courant"""
        self.cartes.append(carte)

    def deplacer_cartes(self, main, nombre):
        """ enlève les nombres première carte du paquet courant et l'ajoute à la main main """
        for i in range(nombre):
            main.ajouter_carte(self.pop_carte())

    def remove_carte(self, carte: Carte):
        """ enlève la carte carte du paquet courant si présente, rien sinon """
        for i, card in enumerate(self.cartes):
            if card == carte:
                self.cartes.pop(i)
                break

    def remove_cartes(self, cartes: list):
        """ enlève les cartes de la liste cartes du paquet courant si présente, rien sinon """
        for carte in cartes:
            for i, card in enumerate(self.cartes):
                if card == carte:
                    self.cartes.pop(i)
                    break


class Main(Paquet):
    """Représente une main au jeu de cartes."""

    # à l'intérieur de la classe Main :
    def __init__(self, cartes):
        self.cartes = []
        for carte in cartes:
            self.cartes.append(carte)

    def __str__(self):
        s = ""
        for carte in self.cartes:
            s += carte.__str__() + "\n"
        return s

    def get_value(self):
        value = 0
        nbr_as = 0

        for carte in self.cartes:
            if isinstance(carte.get_value(), int):
                value += carte.get_value()
            else:  # it's an as
                nbr_as += 1

        value += nbr_as  # 1 points par as
        for i in range(nbr_as):
            # 10 points supplémentaire si inférieur ou égale à 21
            if value + 10 <= 21:
                value += 10

        return value

    def is_splittable(self):
        if len(self.cartes) == 2 and self.cartes[0].get_value() == self.cartes[1].get_value():
            return True
        else:
            return False

    def is_bj(self):
        if len(self.cartes) == 2 and self.get_value() == 21:
            return True
        else:
            return False

    def is_assurance(self):
        if len(self.cartes) == 1 and isinstance(self.cartes[0].get_value(), tuple):
            return True
        else:
            return False


