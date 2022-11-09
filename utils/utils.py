from cartes.paquet import Main


def key_main(main_joueur: Main, main_croupier: Main):
    """
    Pre : la main du joueur contient 2 cartes ou plus, la main du croupier à toujours une seul carte
    :param main_joueur:
    :param main_croupier:
    :return: un string représentant la main joueur-croupier
    """

    main_joueur_value = main_joueur.get_value()
    main_croupier_value = main_croupier.get_value()

    if len(main_croupier.cartes) == 1 and main_croupier_value == 11:  # it's a solo As
        key_croupier = "A"
    else:
        key_croupier = str(main_croupier_value)

    # Calcule la valeur de la main du joueur comme si l'as valait 1
    value_with_as_for_1 = 0
    for carte in main_joueur.cartes:
        if isinstance(carte.get_value(), int):
            value_with_as_for_1 += carte.get_value()
        else:  # it's an as
            value_with_as_for_1 += 1

    if value_with_as_for_1 != main_joueur_value:  # there is an As that count for 11
        if main_joueur.is_splittable():
            key_joueur = "A-A"
        else:
            key_joueur = "A-" + str(main_joueur_value-11)
    else:  # no As as 11 in hand
        if main_joueur.is_splittable():
            split_value = main_joueur.cartes[0].get_value()
            key_joueur = str(split_value) + "-" + str(split_value)
        else:
            key_joueur = str(main_joueur_value)

    return key_joueur + "_" + key_croupier


def joueur_win(main_joueur: Main, main_croupier: Main, assurance=False):
    """
    L'assurance mise toujours 0.5 de la mise initial on gagne si le croupier fait BJ
    :param main_joueur:
    :param main_croupier:
    :param assurance:
    :return: L'espérance de gain : 0.5 si assurance réussie, 1.5, si joueur gagne avec bj, 1 si le joueur gagne, 0 si égalité, -1 si perdu, -0.5 si assurance raté
    """

    if assurance:
        if main_croupier.is_bj():
            if main_joueur.is_bj():
                return 0.5
            else:
                return 0
        else:
            return joueur_win(main_joueur, main_croupier, assurance=False) - 0.5

    if main_joueur.is_bj():
        if main_croupier.is_bj():
            return 0
        else:
            return 1.5

    value_joueur = main_joueur.get_value()
    value_croupier = main_croupier.get_value()

    if value_joueur > 21:
        return -1
    elif value_croupier > 21:
        return 1
    elif value_joueur > value_croupier:
        return 1
    elif value_joueur == value_croupier:
        return 0
    else:
        return -1
