# Politique de sécurité

## Signaler une vulnérabilité

Merci de ne pas publier publiquement une vulnérabilité exploitable, un secret, un token, un mot de passe ou des données sensibles dans une issue ou une Pull Request.

Pour un signalement de sécurité :

1. préparez une description précise du problème ;
2. indiquez les versions ou commits concernés ;
3. fournissez des étapes de reproduction minimales ;
4. évitez d'inclure des données privées réelles ;
5. utilisez en priorité les fonctions privées de signalement de sécurité de GitHub lorsqu'elles sont disponibles sur le dépôt.

Si aucun canal privé n'est disponible, contactez le mainteneur du dépôt directement via son profil GitHub avant de publier les détails techniques.

## Correctifs

Les correctifs de sécurité doivent rester aussi ciblés que possible et inclure, lorsque c'est pertinent, un test empêchant la régression.

## Secrets

Ne commitez jamais :

- fichiers `.env` ;
- clés API ;
- secrets Django ;
- tokens GitHub ;
- mots de passe ;
- bases de données locales contenant des données réelles.
