# Package NLP
***

## Informations
> Initié le : 02/03/2023

> Interlocuteurs : Marine CERCLIER, Grégory GAUTHIER, Tangi LE TALLEC, Alan BIGNON, Islem EZZINE 

> Dans le cadre du projet interne DataScience Package NLP


## Description
L'objectif de ce projet est d'avoir un package NLP permettant d'effectuer différentes tâches de traitement du langage naturel de manière simple et configurable.
Vous pouvez y retrouver différents dossiers et eléments dont chacun répond à des objectifs précis :

* dossier nlppackage : Les différents scripts Python nécessaires au fonctionnement du projet sont enregistrés dans ce dossier.
* fichier requirements.txt : Il contient les packages présents sur l'environnement de travail du développeur et qui sont donc nécessaires au bon fonctionnement du code.
* fichier LICENSE : Spécifie par quelle license juridique est couvert notre projet. 
* fichier README.md : C'est le présent fichier. Il constitue la documentation principale du projet, c'est-à-dire celle qui doit être lue en premier par un utilisateur qui veut comprendre de quoi le projet traite.

## Présentation de la Class NLP
La permet de choisirs entre deux bibliothèques populaires pour le NLP, nltk et spacy. 
Les principales fonctionnalités de cette classe sont :

* Initialisation avec le choix du package NLP à utiliser (nltk ou spacy)
* Tokenization du texte à l'aide du tokenizer sélectionné lors de l'initialisation de la classe
* Nettoyage des mots vides (stop words) en français en ajoutant ou supprimant des mots vides spécifiques
* Conversion du texte en minuscules
* Nettoyage du texte en supprimant tous les caractères spéciaux, sauf ceux spécifiés dans l'argument exception, et en option, en conservant les chiffres
* Suppression des accents d'un texte en les remplaçant par les lettres correspondantes sans accent
* Lemmatisation du texte en tenant compte des exceptions de lemmatisation, en conservant ou non les chiffres, et en excluant certains types de mots

