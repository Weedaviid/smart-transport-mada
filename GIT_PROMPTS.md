# Prompts Git utiles (FR)

Copie-colle ces prompts quand tu veux te faire guider rapidement.

## 1) Démarrer une nouvelle fonctionnalité en branche

```text
Aide-moi à créer une nouvelle branche Git pour une fonctionnalité nommée <nom-feature>, puis donne-moi les commandes pour push la branche sur GitHub.
```

## 2) Voir ce qui a changé avant commit

```text
Montre-moi les commandes Git pour vérifier les fichiers modifiés, voir le diff, et décider quoi ajouter au commit.
```

## 3) Commit propre avec bon message

```text
Propose-moi un message de commit clair (style Conventional Commits) pour mes changements, puis donne les commandes git add/commit.
```

## 4) Mettre a jour ma branche locale

```text
Je suis sur la branche <nom-branche>. Donne-moi les commandes pour recuperer les changements distants sans casser mon historique.
```

## 5) Push mes changements

```text
Donne-moi les commandes pour pousser ma branche actuelle vers GitHub (premier push et push suivants).
```

## 6) Resoudre un rejet de push (fetch first)

```text
J'ai l'erreur "failed to push some refs" ou "fetch first". Guide-moi pas a pas pour corriger sans perdre mes changements.
```

## 7) Revenir en arriere en securite

```text
Explique-moi la difference entre git restore, git reset, et git revert, puis donne la bonne commande pour annuler <cas exact>.
```

## 8) Ouvrir une Pull Request

```text
Je viens de pousser la branche <nom-branche>. Donne-moi le workflow pour ouvrir une Pull Request propre vers main.
```

## 9) Workflow quotidien (checklist)

```text
Donne-moi une checklist Git quotidienne en 6 etapes: update, coder, verifier, commit, push, PR.
```

## 10) Aide diagnostique rapide

```text
Je te donne la sortie de git status et git log --oneline --decorate -n 10. Dis-moi exactement quoi faire ensuite.
```

---

## Commandes de base (rappel rapide)

```bash
git pull origin main
git checkout -b feature/ma-feature
# coder...
git status
git add .
git commit -m "feat: ma nouvelle feature"
git push -u origin feature/ma-feature
```
