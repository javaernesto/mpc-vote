# mpc-vote

## Présentation MPC Mazars

### Contexte
L'entreprise C a une richesse initiale `c` (positive ou négative).

Les entreprises S1 et S2 envoient des flux `s1` et `s2` vers C (positifs ou negatifs). 

Les trois entreprises "partagent" les valeurs `c`, `s1` et `s2`, mais de façon "cryptée", donc personne ne peut voir ces valeurs en clair. Par exemple, S2 ne peut pas dechiffrer `s1`.

Un an plus tard, l'auditeur A veut savoir si C est solvable. Cela se résume à un bit d'information `b`, qui dit si `c + s1 + s2` est positif ou non. Mais l'entreprise C ne veut pas jouer le jeu et ne montre rien de ses comptes. Quant aux entreprises S1 et S2, elles ne veulent dévoiler à personne les montants des flux `s1` et `s2`.

Grâce à un protocole cryptographique entre les participants S1, S2 et A, en deux échanges de messages, le résultat b va s'afficher sur l'écran de l'auditeur A. Les participants n'auront rien appris d'autre, notamment S1 et S2 n'auront même pas appris le résultat `b`.

### Script Python
Pour lancer le programme, ouvrir quatre terminaux (on peut utiliser aussi sous Linux le programme `tmux` qui permet de sous-diviser un terminal en plusieurs sous-terminaux).

Lancer, dans l'ordre, chaque ligne dans un terminal différent :
```
python auditeur.py
python server1.py
python server2.py
python client.py
```

