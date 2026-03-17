# Guide Git pratique (FR)

Ce fichier contient les lignes a taper dans le terminal et ce qu'elles font.

## 1) Demarrer une nouvelle branche

	git pull origin main

Recupere les derniers changements de la branche principale avant de commencer.

	git checkout -b feature/ma-feature

Cree une nouvelle branche et bascule dessus.

	git push -u origin feature/ma-feature

Publie la branche sur GitHub et memorise la destination de push pour la suite.

## 2) Voir les changements en cours

	git status

Affiche les fichiers modifies, ajoutes ou non suivis.

	git diff

Affiche les differences non ajoutees au commit.

	git diff --staged

Affiche les differences deja ajoutees au commit.

## 3) Committer tes modifications

	git add .

Ajoute tous les changements au prochain commit.

	git commit -m "feat: description courte"

Cree un commit avec un message clair.

## 4) Mettre a jour ta branche avant push

	git pull --rebase origin main

Rejoue tes commits locaux au-dessus de la version distante la plus recente pour garder un historique propre.

## 5) Envoyer ton travail sur GitHub

	git push

Envoie tes commits vers la branche distante associee.

	git push origin main

Envoie explicitement vers main quand tu travailles directement sur main.

## 6) Corriger un rejet de push (fetch first)

	git pull --rebase origin main

Integre les changements distants avant de pousser.

	git push origin main

Renvoie tes commits apres integration.

Si Git signale un conflit:

	git add .
	git rebase --continue

Marque les conflits comme resolus puis continue le rebase.

## 7) Annuler proprement selon le besoin

	git restore nom_fichier

Annule les changements non commits d'un fichier.

	git reset --soft HEAD~1

Annule le dernier commit en gardant les changements dans la zone de travail.

	git revert <hash_commit>

Cree un nouveau commit qui annule un commit deja publie.

## 8) Workflow quotidien recommande

	git pull origin main
	git checkout -b feature/ma-feature
	git status
	git add .
	git commit -m "feat: ma fonctionnalite"
	git push -u origin feature/ma-feature

Sequence simple pour travailler proprement et publier sans surprise.
