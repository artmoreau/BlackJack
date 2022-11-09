class Carte:
    """Représente une carte à jouer standard."""

    noms_couleurs = [
        'pique',
        'trèfle',
        'carreau',
        'coeur',
    ]
    noms_valeurs = [
        None,
        'as',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        '10',
        'valet',
        'dame',
        'roi',
    ]
    valeurs = [
        None,
        (1, 11),
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        10,
        10,
        10,
    ]

    def __init__(self, couleur: int, valeur: int):
        self.couleur = couleur
        self.valeur = valeur

    def __str__(self):
        return f'{Carte.noms_valeurs[self.valeur]} de {Carte.noms_couleurs[self.couleur]}'

    def __eq__(self, other):
        """ défini l'opérateur de comparaison entre 2 cartes """
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    def get_value(self):
        return Carte.valeurs[self.valeur]
