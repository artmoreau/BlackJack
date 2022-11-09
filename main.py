import argparse
import logging

from cartes.carte import Carte
from cartes.paquet import Paquet, Main
from utils.decision_param import decision, decision_tire
from utils.utils import key_main, joueur_win

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


def distribue():
    paquet = Paquet(nbr_paquet=8)
    main_joueur = Main([])
    main_croupier = Main([])
    paquet.shuffle()
    paquet.deplacer_cartes(main_croupier, nombre=1)
    paquet.deplacer_cartes(main_joueur, nombre=2)
    return main_joueur, main_croupier


def play_hand(main_joueur: Main, main_croupier: Main, decision_dict=decision, decision_dict_tire=decision_tire):
    """
    joue une main
    :param main_joueur:  main de 2 cartes
    :param main_croupier: main d'une carte
    :param decision_dict:
    :return: le ratio_gain dépendant de la mise initial
    """

    all_played_cartes = main_joueur.cartes + main_croupier.cartes
    paquet = Paquet(nbr_paquet=8)
    paquet.remove_carte(all_played_cartes)
    paquet.shuffle()

    key = key_main(main_joueur, main_croupier)

    if decision_dict.get(key) == 'split':
        main1 = Main([Carte(0, main_joueur.cartes[0].valeur)])
        main2 = Main([Carte(0, main_joueur.cartes[1].valeur)])

        if key.startswith("A-A"):  # it's a double as only one card can be tire
            paquet.deplacer_cartes(main1, nombre=1)
            paquet.deplacer_cartes(main2, nombre=1)
        else:
            while decision_dict_tire.get(key, False):
                paquet.deplacer_cartes(main1, nombre=1)
                key = key_main(main1, main_croupier)

            while decision_dict_tire.get(key, False):
                paquet.deplacer_cartes(main2, nombre=1)
                key = key_main(main2, main_croupier)

        while main_croupier.get_value() < 17:
            paquet.deplacer_cartes(main_croupier, nombre=1)

        ratio_gain1 = min(joueur_win(main1, main_croupier), 1)  # pas de BJ après split
        ratio_gain2 = min(joueur_win(main2, main_croupier), 1)  # pas de BJ après split
        ratio_gain = ratio_gain1 + ratio_gain2
        logger.debug(f"main joueur split :\n{main1.__str__()}---\n{main2.__str__()}")
        logger.debug(f"main croupier :\n{main_croupier.__str__()}")

    elif decision_dict.get(key) == 'double':
        paquet.deplacer_cartes(main_joueur, nombre=1)

        while main_croupier.get_value() < 17:
            paquet.deplacer_cartes(main_croupier, nombre=1)

        ratio_gain = 2*joueur_win(main_joueur, main_croupier)
        logger.debug(f"main joueur double :\n{main_joueur.__str__()}")
        logger.debug(f"main croupier :\n{main_croupier.__str__()}")

    elif decision_dict.get(key) == 'assure':
        while decision_dict_tire.get(key, False):
            paquet.deplacer_cartes(main_joueur, nombre=1)
            key = key_main(main_joueur, main_croupier)

        while main_croupier.get_value() < 17:
            paquet.deplacer_cartes(main_croupier, nombre=1)

        ratio_gain = joueur_win(main_joueur, main_croupier, assurance=True)
        logger.debug(f"main joueur assure:\n{main_joueur.__str__()}")
        logger.debug(f"main croupier :\n{main_croupier.__str__()}")

    else:
        while decision_dict_tire.get(key, False):
            paquet.deplacer_cartes(main_joueur, nombre=1)
            key = key_main(main_joueur, main_croupier)

        while main_croupier.get_value() < 17:
            paquet.deplacer_cartes(main_croupier, nombre=1)

        ratio_gain = joueur_win(main_joueur, main_croupier)
        logger.debug(f"main joueur :\n{main_joueur.__str__()}")
        logger.debug(f"main croupier :\n{main_croupier.__str__()}")

    return ratio_gain


def play(nbr_partie, mise):
    gain = 0
    for i in range(nbr_partie):
        main_joueur, main_croupier = distribue()
        logger.debug(f"main de départ : {key_main(main_joueur, main_croupier)}")
        ratio_gain = play_hand(main_joueur, main_croupier)
        gain += mise * ratio_gain
        logger.debug(f"ratio gain : {ratio_gain}")
        logger.debug("------------------------------------------------")
    return gain


if __name__ == '__main__':

    #  Init args
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--mise",
        dest="mise",
        action="store",
        required=False,
        help="mise per hand play",
        type=int,
        default=1,
    )
    parser.add_argument(
        "-n",
        "--nbr_partie",
        dest="nbr_partie",
        action="store",
        required=False,
        help="mise per hand play",
        type=int,
        default=1000,
    )
    args = parser.parse_args()

    mise = args.mise
    nbr_partie = args.nbr_partie

    gain = play(nbr_partie, mise)

    logger.info(f"main jouées : {nbr_partie},\tmise : {mise}")
    logger.info(f"gain total : {gain}")
    logger.info(f"espérance : {gain/nbr_partie}")
