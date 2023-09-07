# Thème DSFR pour MkDocs DSFR

> ATTENTION : Ce thème est uniquement destiné à être utilisé pour les sites et applications officiels des services publics français. Son objectif principal est de faciliter l'identification des sites gouvernementaux pour les citoyens.

[Mentions légales](https://www.systeme-de-design.gouv.fr/cgu/).

## Démarrage rapide

Pour expérimenter rapidement mkdocs avec le DSFR, vous pouvez cloner le [projet d'exemple](https://gitlab-forge.din.developpement-durable.gouv.fr/pub/numeco/mkdocs-dsfr-exemple).

## Configuration du thème DSFR MkDocs

Ce document décrit les différentes options de configuration pour le thème DSFR MkDocs.
Dans votre fichier de configuration `mkdocs.yml`, vous pouvez définir les options de thème pour personnaliser
votre site en utilisant l'exemple suivant :

```yaml
theme:
  menulateral: true
  intitule: "Intitulé"
  include_search_page: true
  header:
    titre: "Titre"
    sous_titre: "Sous-titre"
  footer:
    description: "Description à modifier"
    links:
      - name: legifrance.gouv.fr
        url: https://legifrance.gouv.fr
      - name: gouvernement.fr
        url: https://gouvernement.fr
      - name: service-public.fr
        url: https://service-public.fr
      - name: data.gouv.fr
        url: https://data.gouv.fr
```

## Options de Thème

### `name`

Le nom du thème. Il doit être défini sur 'mkdocs'.

### `locale`

La locale pour le thème. Il est défini sur 'fr' pour le français.

### `custom_dir`

Le répertoire du thème personnalisé. Il doit être défini sur 'dsfr/'.

### `menulateral`

Valeur booléenne pour afficher ou masquer le menu latéral. Définissez-le sur `true` ou `false`.

### `intitule`

Cette option définit le titre principal dans l'en-tête et le pied de page.

### `include_search_page`

Valeur booléenne pour afficher ou masquer la barre de recherche dans l'en-tête. Définissez-le sur `true` ou `false`.

## Options d'En-tête

### `titre`

Cela définit le titre qui apparaît dans l'en-tête de la page.

### `soustitre`

Cela définit le sous-titre qui apparaît sous le titre dans l'en-tête de la page.

## Options de Pied de Page

### `description`

Cela définit une description qui apparaît dans le pied de page.

### `links`

Cette option vous permet de définir une liste de liens qui apparaîtront dans le pied de page. Chaque lien doit être un
dictionnaire avec des clés `name` et `url`.

## Notes de version

### Version 0.5.3 (DSFR 1.10.1)

* Correction documentation pour la fonction recherche
* Mise à jour DSFR

### Version 0.5.2 (DSFR 1.10.0)

* Correction bug technique lié à la fonction recherche

### Version 0.5.1 (DSFR 1.10.0)

* Corrections pour prise en charge de la recherche

### Version 0.5.0 (DSFR 1.10.0)

* Prise en charge du texte barré
* Prise en charge des checkboxes
* Mise à jour du DSFR

### Version 0.4.0 (DSFR 1.9.3)

* Ajout de variables de configuration

### Version 0.3.1 (DSFR 1.9.3)

* Correction de problèmes d'import et d'affichage

### Version 0.3.0 (DSFR 1.9.3 Juin 2023)

* Ajout du composant paramètre d'affichage dans le footer pour la gestion des thèmes dark et light

### Version 0.2.0 (June 2023)

* Initial experimental version
