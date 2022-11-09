import copy
import logging

from cartes.carte import Carte
from cartes.paquet import Paquet, Main
from utils import joueur_win, key_main
from decision_param import decision_tire_one, decision_tire, decision_doublable, decision_splitable, decision_assurable

#######################################################################################################################
# Init logger

# création de l'objet logger qui va nous servir à écrire dans les logs
logger = logging.getLogger(__name__)  # __name__ est le nom du module, n'affiche que les logs de ce module
logger.setLevel(logging.DEBUG)

# création d'un formateur qui va ajouter le temps, le niveau de chaque message quand on écrira un message dans le log
# formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# création d'un  handler qui va rediriger chaque écriture de log sur la console qu'on ajoute au logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
# stream_handler.setFormatter(formatter)
stream_handler.addFilter(logging.Filter(__name__))
logger.addHandler(stream_handler)
#######################################################################################################################


def display_dict(tire_one=False, tire=False, doublable=False, splittable=False, assurable=False, nbr_try=10):

    if tire_one:
        compute_dict_is_better_tire_one(nbr_try=nbr_try)  # ok with 50000
    if tire:
        compute_dict_is_better_tire(basic_decision_dict_tire=decision_tire_one, nbr_try=nbr_try)
    if doublable:
        compute_dict_is_doublable(decision_dict_tire=decision_tire, nbr_try=nbr_try)
    if splittable:
        compute_dict_is_splittable(decision_dict_tire=decision_tire, nbr_try=nbr_try)
    if assurable:
        compute_dict_is_assurable(decision_dict_tire=decision_tire, nbr_try=nbr_try)


def compute_decision_dict(decision_dict_tire, decision_dict_splitable, decision_dict_doublable, decision_dict_assurable):
    """
    :param decision_dict_tire:
    :param decision_dict_splitable:
    :param decision_dict_doublable:
    :param decision_dict_assurable:
    :return: The full decision dict
    """
    dico_result = {}

    for valeur1 in range(1, 14):
        c1 = Carte(0, valeur1)
        for valeur2 in range(1, 14):
            c2 = Carte(0, valeur2)
            main_joueur = Main([c1, c2])

            for valeur3 in range(1, 14):
                c3 = Carte(0, valeur3)
                main_croupier = Main([c3])

                key = key_main(main_joueur, main_croupier)

                if key in dico_result:  # don't compute to hand with the same key
                    continue

                if decision_dict_splitable.get(key, False):
                    decision = "split"
                elif decision_dict_doublable.get(key, False):
                    decision = "double"
                elif decision_dict_assurable.get(key, False):
                    decision = "assure"
                elif decision_dict_tire.get(key, False):
                    decision = "tire"
                else:
                    decision = "reste"

                dico_result[key] = decision

    return dico_result


def compute_dict_is_assurable(decision_dict_tire, nbr_try=100):
    """
    :param decision_dict_tire:
    :param nbr_try:
    :return: a dict containing true or false depending if the key is interressante to assure
    """

    dico_result = {}

    for valeur1 in range(1, 14):

        logger.debug(f"compute_dict_is_assurable : {int(100 * valeur1 / 13)}%")

        c1 = Carte(0, valeur1)
        for valeur2 in range(1, 14):
            c2 = Carte(0, valeur2)
            main_joueur = Main([c1, c2])
            for valeur3 in range(1, 14):
                c3 = Carte(0, valeur3)
                main_croupier = Main([c3])
                key = key_main(main_joueur, main_croupier)

                if key in dico_result:  # don't compute to hand with the same key
                    continue

                decision = compute_is_assurable(main_joueur, main_croupier, decision_dict_tire, nbr_try)  # if main_croupier is not AS it'will return false

                dico_result[key] = decision

    logger.info(f"compute_dict_is_assurable : result :\n{dico_result}\n")

    return dico_result


def compute_is_assurable(main_joueur: Main, main_croupier: Main, decision_dict_tire, nbr_try=100):
    """
    :param main_joueur:
    :param main_croupier:
    :param decision_dict_tire:
    :param nbr_try:
    :return: True si la main est intéressante a assurer False sinon
    """
    if main_croupier.is_assurance():
        esperance = compute_esperance(main_joueur, main_croupier, decision_dict_tire, nbr_try)
        esperance_assurance = compute_esperance(main_joueur, main_croupier, decision_dict_tire, nbr_try, assurance=True)
        if esperance_assurance > esperance:
            return True
        else:
            return False
    else:
        return False


def compute_dict_is_splittable(decision_dict_tire, nbr_try=100):
    """
    :param decision_dict_tire:
    :param nbr_try:
    :return: a dict containing true or false depending if the key is interressante to split
    """

    dico_result = {}

    for valeur1 in range(1, 14):

        logger.debug(f"compute_dict_is_splittable : {int(100 * (valeur1-1) / 13)}%")

        c1 = Carte(0, valeur1)
        for valeur2 in range(1, 14):
            c2 = Carte(0, valeur2)
            main_joueur = Main([c1, c2])

            for valeur3 in range(1, 14):
                c3 = Carte(0, valeur3)
                main_croupier = Main([c3])

                key = key_main(main_joueur, main_croupier)

                if key in dico_result:  # don't compute to hand with the same key
                    continue

                decision = compute_is_splittable(main_joueur, main_croupier, decision_dict_tire, nbr_try)

                dico_result[key] = decision

    logger.info(f"compute_dict_is_splittable : result :\n{dico_result}\n")

    return dico_result


def compute_is_splittable(main_joueur: Main, main_croupier: Main, decision_dict_tire, nbr_try=100):
    """
    :param main_joueur:
    :param main_croupier:
    :param decision_dict_tire:
    :param nbr_try:
    :return: True si la main est intéressante a splitter False sinon
    """
    if main_joueur.is_splittable():
        esperance = compute_esperance(main_joueur, main_croupier, decision_dict_tire, nbr_try)
        main_joueur_split = Main([Carte(0, main_joueur.cartes[0].valeur)])
        esperance_split = compute_esperance(main_joueur_split, main_croupier, decision_dict_tire, nbr_try)
        if esperance_split > esperance:
            return True
        else:
            return False
    else:
        return False


def compute_dict_is_doublable(decision_dict_tire, nbr_try=100):
    """
    :param decision_dict_tire:
    :param nbr_try:
    :return: a dict containing true or false depending if the key is interressante to double
    """
    dico_result = {}

    for valeur1 in range(1, 14):

        logger.debug(f"compute_dict_is_doublable : {int(100 * (valeur1-1) / 13)}%")

        c1 = Carte(0, valeur1)
        for valeur2 in range(1, 14):
            c2 = Carte(0, valeur2)
            main_joueur = Main([c1, c2])

            for valeur3 in range(1, 14):
                c3 = Carte(0, valeur3)
                main_croupier = Main([c3])

                key = key_main(main_joueur, main_croupier)

                if key in dico_result:  # don't compute two hand with the same key
                    continue

                decision = compute_is_doublable(main_joueur, main_croupier, decision_dict_tire, nbr_try)

                dico_result[key] = decision

    logger.info(f"compute_dict_is_doublable : result :\n{dico_result}\n")

    return dico_result


def compute_is_doublable(main_joueur: Main, main_croupier: Main, decision_dict_tire, nbr_try=100):
    """
    PS : Après avoir doublé, on doit tirer une et une seul carte supplémentaire
    (pour ça qu'on utilise compute_proba_if_tire_one)
    :param main_joueur:
    :param main_croupier:
    :param decision_dict_tire:
    :param nbr_try:
    :return: True si la main est intéressante a doubler False sinon
    """
    key = key_main(main_joueur, main_croupier)
    esperance = compute_esperance_if_tire_one(main_joueur, main_croupier, nbr_try)

    if decision_dict_tire.get(key):  # better tire
        return esperance > 0
    else:  # better reste
        return 2*esperance > compute_esperance_if_reste(main_joueur, main_croupier, nbr_try)


def compute_esperance(main_joueur: Main, main_croupier: Main, decision_dict_tire, nbr_try=100, assurance=False):
    """
    :param decision_dict_tire:
    :param main_joueur:
    :param main_croupier:
    :param nbr_try:
    :param assurance:
    :return: a tuple representing the probability of winning, egal, loss, according to the arg decision_dict.
    """

    esperance = 0

    all_played_cartes = main_joueur.cartes + main_croupier.cartes

    for i in range(nbr_try):

        main_croupier_copy = copy.deepcopy(main_croupier)
        main_joueur_copy = copy.deepcopy(main_joueur)

        paquet = Paquet(nbr_paquet=8)
        paquet.remove_carte(all_played_cartes)
        paquet.shuffle()

        while len(main_joueur_copy.cartes) < 2:
            paquet.deplacer_cartes(main_joueur_copy, nombre=1)

        key = key_main(main_joueur_copy, main_croupier_copy)

        while decision_dict_tire.get(key, False):
            paquet.deplacer_cartes(main_joueur_copy, nombre=1)
            key = key_main(main_joueur_copy, main_croupier_copy)

        while main_croupier_copy.get_value() < 17:
            paquet.deplacer_cartes(main_croupier_copy, nombre=1)

        esperance += joueur_win(main_joueur_copy, main_croupier_copy, assurance)

    return esperance/nbr_try


def compute_dict_is_better_tire(basic_decision_dict_tire, nbr_try=100):
    """
    :param basic_decision_dict_tire: The decision dict computed by compute_dict_is_better_tire_one
    :param nbr_try:
    :return: a dico containing where entry is key_main and the value is True or False depending if it's better to
    tire. This dict take care of AS
    """

    dico_result = basic_decision_dict_tire

    c1 = Carte(0, 1)  # it's a AS
    for j, valeur2 in enumerate([1, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]):

        logger.debug(f"compute_dict_is_better_tire : {int(100 * j / 13)}%")

        c2 = Carte(0, valeur2)
        main_joueur = Main([c1, c2])
        for valeur3 in range(1, 14):
            c3 = Carte(0, valeur3)
            main_croupier = Main([c3])

            key = key_main(main_joueur, main_croupier)

            if key in dico_result:
                continue

            decision = is_better_tire(main_joueur, main_croupier, dico_result, nbr_try)

            dico_result[key] = decision

    logger.info(f"compute_dict_is_better_tire : result :\n{dico_result}\n")

    return dico_result


def is_better_tire(main_joueur: Main, main_croupier: Main, basic_decision_dict_tire, nbr_try=100, assurance=False):
    """
    :param main_joueur:
    :param main_croupier:
    :param basic_decision_dict_tire:
    :param nbr_try:
    :param assurance:
    :return: True si il vaut mieux tirer une carte de plus, False sinon, selon le decision_dict
    """

    if compute_esperance_if_tire(main_joueur, main_croupier, basic_decision_dict_tire, nbr_try, assurance) > compute_esperance_if_reste(main_joueur, main_croupier, nbr_try, assurance):
        return True
    else:
        return False


def compute_esperance_if_tire(main_joueur: Main, main_croupier: Main, decision_dict_tire, nbr_try=100, assurance=False):
    """
    This function is use to add de decision for player hand with AS
    :param decision_dict_tire:
    :param main_joueur:
    :param main_croupier:
    :param nbr_try:
    :param assurance:
    :return: a tuple representing the probability of winning, egal, loss, if tire one more and then
    continue to tire according to the arg decision_dict_tire.
    """

    esperance = 0

    all_played_cartes = main_joueur.cartes + main_croupier.cartes

    for i in range(nbr_try):

        main_croupier_copy = copy.deepcopy(main_croupier)
        main_joueur_copy = copy.deepcopy(main_joueur)

        paquet = Paquet(nbr_paquet=8)
        paquet.remove_carte(all_played_cartes)
        paquet.shuffle()

        paquet.deplacer_cartes(main_joueur_copy, nombre=1)

        # For case of a empty hand player
        while len(main_joueur_copy.cartes) < 2:
            paquet.deplacer_cartes(main_joueur_copy, nombre=1)

        key = key_main(main_joueur_copy, main_croupier_copy)

        while decision_dict_tire.get(key, False):
            paquet.deplacer_cartes(main_joueur_copy, nombre=1)
            key = key_main(main_joueur_copy, main_croupier_copy)

        while main_croupier_copy.get_value() < 17:
            paquet.deplacer_cartes(main_croupier_copy, nombre=1)

        esperance += joueur_win(main_joueur_copy, main_croupier_copy, assurance)

    return esperance/nbr_try


def compute_dict_is_better_tire_one(nbr_try=100):
    """
    The dico result don't take care of the player main with As
    :param nbr_try:
    :return: a dico containing where entry is key_main and the value is True or False depending if it's better to
    tire one card more
    """
    dico_result = {}

    for valeur1 in range(2, 14):

        logger.debug(f"compute_dict_is_better_tire_one : {int(100 * (valeur1-2) / 12)}%")

        c1 = Carte(0, valeur1)
        for valeur2 in range(2, 14):
            c2 = Carte(0, valeur2)
            main_joueur = Main([c1, c2])

            for valeur3 in range(1, 14):
                c3 = Carte(0, valeur3)
                main_croupier = Main([c3])

                key = key_main(main_joueur, main_croupier)

                if key in dico_result:  # don't compute to hand with the same key
                    continue

                decision = is_better_tire_one(main_joueur, main_croupier, nbr_try)

                dico_result[key] = decision

    logger.info(f"compute_dict_is_better_tire_one : result :\n{dico_result}\n")

    return dico_result


def is_better_tire_one(main_joueur: Main, main_croupier: Main, nbr_try=100, assurance=False):
    """
    This function make sens if you don't have AS in hand.
    :param main_joueur:
    :param main_croupier:
    :param nbr_try:
    :param assurance:
    :return: True si il vaut mieux tirer une carte de plus, False sinon
    """
    for carte in main_joueur.cartes:
        if isinstance(carte.get_value(), tuple):  # it's an as
            return "dont know"

    if main_joueur.get_value() < 12:
        return True
    elif main_joueur.get_value() > 17:
        return False
    else:
        if compute_esperance_if_tire_one(main_joueur, main_croupier, nbr_try, assurance) > compute_esperance_if_reste(main_joueur, main_croupier, nbr_try, assurance):
            return True
        else:
            return False


def compute_esperance_if_tire_one(main_joueur: Main, main_croupier: Main, nbr_try=100, assurance=False):
    """
    This function make sens if you don't have AS in hand.

    :param main_joueur:
    :param main_croupier:
    :param nbr_try:
    :param assurance:
    :return: a tuple representing the probability of winning, egal, loss, if tire only one card more
    """

    esperance = 0

    all_played_cartes = main_joueur.cartes + main_croupier.cartes

    for i in range(nbr_try):

        main_croupier_copy = copy.deepcopy(main_croupier)
        main_joueur_copy = copy.deepcopy(main_joueur)

        paquet = Paquet(nbr_paquet=8)
        paquet.remove_carte(all_played_cartes)
        paquet.shuffle()

        paquet.deplacer_cartes(main_joueur_copy, nombre=1)

        while main_croupier_copy.get_value() < 17:
            paquet.deplacer_cartes(main_croupier_copy, nombre=1)

        esperance += joueur_win(main_joueur_copy, main_croupier_copy, assurance)

    return esperance/nbr_try


def compute_esperance_if_reste(main_joueur: Main, main_croupier: Main, nbr_try=100, assurance=False):
    """
    :param main_joueur:
    :param main_croupier:
    :param nbr_try:
    :param assurance:
    :return: a tuple representing the probability of winning, egal, loss, if you rest
    """

    esperance = 0

    all_played_cartes = main_joueur.cartes + main_croupier.cartes

    for i in range(nbr_try):

        main_croupier_copy = copy.deepcopy(main_croupier)

        paquet = Paquet(nbr_paquet=8)
        paquet.remove_carte(all_played_cartes)
        paquet.shuffle()

        while main_croupier_copy.get_value() < 17:
            paquet.deplacer_cartes(main_croupier_copy, nombre=1)

        esperance += joueur_win(main_joueur, main_croupier_copy, assurance)

    return esperance/nbr_try


if __name__ == '__main__':

    display_dict(tire_one=True, tire=True, doublable=True, splittable=True, assurable=True, nbr_try=100)

    print(compute_decision_dict(decision_tire, decision_splitable, decision_doublable, decision_assurable))

