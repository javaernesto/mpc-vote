# mpc-vote

## Présentation MPC Mazars

### Contexte
L'entreprise C a une richesse initiale `c` (positive ou négative). Les entreprises S1 et S2 envoient des flux `s1` et `s2` vers C (positifs ou negatifs).  Les trois entreprises "partagent" les valeurs `c`, `s1` et `s2`, mais de façon "cryptée", donc personne ne peut voir ces valeurs en clair. Par exemple, S2 ne peut pas dechiffrer `s1`.

Un an plus tard, l'auditeur A veut savoir si C est solvable. Cela se résume à un bit d'information `b`, qui dit si `c + s1 + s2` est positif ou non. Mais l'entreprise C ne veut pas jouer le jeu et ne montre rien de ses comptes. Quant aux entreprises S1 et S2, elles ne veulent dévoiler à personne les montants des flux `s1` et `s2`.

Grâce à un protocole cryptographique entre les participants S1, S2 et A, en deux échanges de messages, le résultat `b` va s'afficher sur l'écran de l'auditeur A. Les participants n'auront rien appris d'autre, notamment S1 et S2 n'auront même pas appris le résultat `b`.

### Script Python
Pour lancer le programme, ouvrir quatre terminaux (on peut utiliser sous Linux le programme `tmux` qui permet de sous-diviser un terminal en plusieurs sous-terminaux).

Lancer, dans l'ordre, chaque ligne dans un terminal différent :
```
python auditeur.py
python server1.py
python server2.py
python client.py
```

### Description de l'algorithme
Pendant tout le déroulement du protocole, chaque secret sera partagé avec S1 et S2. Tous les secrets (`c`, `s1`, `s2` et `b`) seront donc partagés en deux parts. Pour partager un secret `x`, il suffit de choisir une valeur aléatoire `r` (un entier positif ou négatif), puis calculer `x - r`. Ainsi, on peut envoyer `x_1 := x - r` à S1 et `x_2 := r` à S2, de façon à ce que ni S1 ni S2 ne puissent connaître `x`, mais puissent le reconstituer en échageant leurs parts et en faisant `x = x_1 + x_2`.

Le protocole se déroule de la façon suivante :

1. L'entreprise C envoie les parts `c_1` et `c_2` de sa richesse `c` aux entreprises S1 et S2 respectivement, comme détaillé plus haut.
2. L'entreprise S1 fait des parts `s1_1` et `s1_2` de `s1`. Elle garde la part `s1_1` et envoie la part `s1_2` à S2.
3. L'entreprise S2 fait de même avec son secret `s2`.
4. Passé un certain temps, l'auditeur A demande à S1 et S2 de calculer des parts de `b` (0 si `c + s1 + s2 >= 0` et 1 sinon). Les entreprises S1 et S2 calculent chacune leur part de `b` et l'envoient à A.
5. L'auditeur A affiche le résultat `b` sur son écran (il a reconstitué le secret grâce aux parts de S1 et de S2).
