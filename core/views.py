from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")


def _render_static_page(request, title, lead, sections):
    return render(
        request,
        "core/static_page.html",
        {
            "page_title": title,
            "page_lead": lead,
            "page_sections": sections,
        },
    )


def contact(request):
    return _render_static_page(
        request,
        "Contact",
        "Vous pouvez joindre l'équipe via les coordonnées ci-dessous.",
        [
            {
                "title": "Adresse email",
                "content": "contact@braincollider.fr",
                "link": "mailto:contact@braincollider.fr",
            },
            {
                "title": "Objet du message",
                "content": "Support technique, remarque sur une page ou demande administrative.",
            },
        ],
    )


def legal_notice(request):
    return _render_static_page(
        request,
        "Mentions légales",
        "Conformément à l'article 6 de la loi n° 2004-575 du 21 juin 2004 pour la confiance dans l'économie numérique (LCEN).",
        [
            {
                "title": "Éditeur du site",
                "content": (
                    "Le site braincollider.fr est édité à titre personnel, à des fins non commerciales, par Ulysse Larger. "
                    "Éditeur non professionnel — particulier."
                ),
            },
            {
                "title": "Objet du site",
                "content": (
                    "Braincollider est une plateforme éducative gratuite dédiée à la préparation aux olympiades de physique. "
                    "Elle propose des problèmes, un classement et des profils publics. "
                    "Le site n'a aucune vocation commerciale et l'accès à tous les contenus est libre et gratuit."
                ),
            },
            {
                "title": "Propriété intellectuelle",
                "content": (
                    "Les contenus pédagogiques publiés sur Braincollider sont originaux et rédigés par l'équipe éditoriale bénévole, "
                    "sauf mention contraire. Ils sont mis à disposition sous licence Creative Commons CC BY-NC-SA 4.0 "
                    "(Attribution — Pas d'utilisation commerciale — Partage dans les mêmes conditions)."
                ),
            },
            {
                "title": "Données personnelles et RGPD",
                "content": (
                    "Braincollider collecte un pseudo, une adresse e-mail et des scores dans le cadre des comptes utilisateurs. "
                    "Seuls le pseudo et le score sont publics. L'e-mail n'est jamais visible. "
                    "Les données sont conservées tant que le compte est actif et supprimées sous 30 jours sur demande. "
                    "Droits d'accès, rectification et suppression à exercer via contact@braincollider.fr. "
                    "Les utilisateurs de moins de 15 ans doivent disposer de l'accord d'un parent ou tuteur légal."
                )
            },
            {
                "title": "Cookies",
                "content": (
                    "Le site utilise uniquement deux cookies techniques strictement nécessaires : "
                    "sessionid (maintien de la session) et csrftoken (protection CSRF). "
                    "Ces cookies ne collectent aucune donnée de traçage et sont exemptés de consentement selon les lignes directrices de la CNIL."
                ),
            },
            {
                "title": "Responsabilité et liens externes",
                "content": (
                    "L'éditeur s'efforce de maintenir des informations exactes mais ne garantit pas l'exhaustivité des contenus. "
                    "Le site peut contenir des liens vers des ressources externes dont l'éditeur ne contrôle pas le contenu."
                ),
            },
            {
                "title": "Affiliation avec les olympiades",
                "content": (
                    "Braincollider propose un entrainement ciblé pour les International Physics Olympiad (IPhO) et les Olympiades de Physique France (OPF), mais n'est affilié à aucune organisation officielle d'olympiades. "
                    "La préparation française peut librement utiliser ces problèmes, sans autorisation préalable."
                ),
            },
        ],
    )


def privacy(request):
    return _render_static_page(
        request,
        "Politique de confidentialité",
        "Cette politique décrit quelles données Braincollider collecte, pourquoi, et quels sont vos droits. Dernière mise à jour : juin 2025.",
        [
            {
                "title": "Responsable du traitement",
                "content": (
                    "Le responsable du traitement des données est Ulysse Larger, éditeur du site braincollider.fr. "
                    "Pour toute question relative à vos données, contactez-nous à contact@braincollider.fr."
                ),
            },
            {
                "title": "Données collectées",
                "content": (
                    "Lors de la création d'un compte, nous collectons : une adresse e-mail (identification et communication), "
                    "un pseudo (affiché publiquement dans le classement), et un mot de passe (stocké chiffré, jamais lisible). "
                    "En cours d'utilisation, nous enregistrons vos scores et votre progression sur les problèmes."
                ),
            },
            {
                "title": "Finalité du traitement",
                "content": (
                    "Vos données sont utilisées exclusivement pour : la gestion de votre compte et de votre session, "
                    "l'affichage du classement public, et le suivi de votre progression personnelle. "
                    "Aucune donnée n'est utilisée à des fins publicitaires, commerciales ou de profilage."
                ),
            },
            {
                "title": "Base légale",
                "content": (
                    "Le traitement repose sur l'exécution du contrat (CGU) que vous acceptez lors de votre inscription, "
                    "conformément à l'article 6(1)(b) du RGPD. "
                    "Pour les utilisateurs de moins de 15 ans, le traitement requiert le consentement d'un parent ou tuteur légal "
                    "conformément à l'article 8 du RGPD et à la loi Informatique et Libertés."
                ),
            },
            {
                "title": "Données rendues publiques",
                "content": (
                    "Seuls votre pseudo et vos scores figurent dans le classement public, visible par tous les visiteurs du site. "
                    "Votre adresse e-mail n'est jamais affichée ni partagée. "
                    "Vous pouvez choisir un pseudo ne permettant pas de vous identifier."
                ),
            },
            {
                "title": "Durée de conservation",
                "content": (
                    "Vos données sont conservées tant que votre compte est actif. "
                    "En cas de demande de suppression, l'ensemble de vos données — y compris votre apparition dans le classement — "
                    "est effacé dans un délai de 30 jours. "
                    "Les données d'un compte inactif depuis plus de 3 ans pourront être supprimées après notification par e-mail."
                ),
            },
            {
                "title": "Cookies",
                "content": (
                    "Le site utilise uniquement deux cookies techniques strictement nécessaires : "
                    "sessionid (maintien de votre session connectée) et csrftoken (protection contre les attaques CSRF). "
                    "Aucun cookie de traçage, publicitaire ou analytique n'est déposé. "
                    "Ces cookies sont supprimés à la déconnexion ou à l'expiration de session."
                ),
            },
            {
                "title": "Hébergement et transfert de données",
                "content": (
                    "Le site est hébergé par OVH, dont les serveurs sont situés dans l'Union européenne. "
                    "Aucune donnée personnelle n'est transférée hors de l'UE."
                ),
            },
            {
                "title": "Vos droits",
                "content": (
                    "Conformément au RGPD (articles 15 à 22), vous disposez des droits suivants sur vos données : "
                    "accès, rectification, effacement (droit à l'oubli), portabilité, limitation du traitement, et opposition. "
                    "Pour exercer ces droits, envoyez une demande à contact@braincollider.fr. "
                    "En cas de réclamation non résolue, vous pouvez saisir la CNIL sur cnil.fr."
                ),
            },
            {
                "title": "Modifications de cette politique",
                "content": (
                    "Cette politique peut être mise à jour pour refléter des évolutions du site ou de la réglementation. "
                    "En cas de modification substantielle, les utilisateurs disposant d'un compte seront informés par e-mail. "
                    "La date de dernière mise à jour est indiquée en haut de cette page."
                ),
            },
        ],
    )
    
def terms(request):
    return _render_static_page(
        request,
        "Conditions générales d'utilisation",
        "En créant un compte ou en utilisant Braincollider, vous acceptez les présentes conditions. Dernière mise à jour : juin 2025.",
        [
            {
                "title": "Objet",
                "content": (
                    "Les présentes conditions générales d'utilisation (CGU) régissent l'accès et l'utilisation du site braincollider.fr, "
                    "plateforme éducative gratuite de préparation aux olympiades de physique, éditée par Ulysse Larger. "
                    "L'utilisation du site vaut acceptation sans réserve des présentes CGU."
                ),
            },
            {
                "title": "Accès au site",
                "content": (
                    "L'accès aux problèmes et au classement est libre et gratuit, sans création de compte. "
                    "La création d'un compte est nécessaire pour enregistrer sa progression et apparaître au classement. "
                    "Les utilisateurs de moins de 15 ans doivent disposer de l'accord d'un parent ou tuteur légal. "
                    "Braincollider se réserve le droit de suspendre ou interrompre l'accès au site à tout moment, sans préavis."
                ),
            },
            {
                "title": "Création de compte",
                "content": (
                    "Chaque utilisateur ne peut disposer que d'un seul compte. "
                    "Vous êtes responsable de la confidentialité de vos identifiants et de toute activité réalisée depuis votre compte. "
                    "En cas de compromission de votre compte, vous vous engagez à en informer l'équipe sans délai à contact@braincollider.fr. "
                    "Le pseudo choisi doit être décent et ne pas usurper l'identité d'une autre personne."
                ),
            },
            {
                "title": "Profils publics et classement",
                "content": (
                    "En créant un compte, vous acceptez que votre pseudo et vos scores soient affichés publiquement dans le classement, "
                    "visible par tous les visiteurs du site, y compris les non-inscrits. "
                    "Vous pouvez à tout moment demander la suppression de votre compte, ce qui entraîne le retrait de votre "
                    "apparition dans le classement et dans les bases de données sous 30 jours."
                ),
            },
            {
                "title": "Contenu soumis par les utilisateurs",
                "content": (
                    "Les utilisateurs peuvent publier des commentaires et proposer des solutions aux problèmes. "
                    "Vous êtes seul responsable des contenus que vous publiez. "
                    "En publiant un contenu, vous accordez à Braincollider une licence gratuite, non exclusive, pour l'afficher sur le site. "
                    "Sont interdits : les contenus hors-sujet, injurieux, discriminatoires, copiés sans attribution, "
                    "ou constituant de la tromperie (fausses solutions, spoilers non signalés). "
                    "L'équipe se réserve le droit de supprimer tout contenu sans préavis."
                ),
            },
            {
                "title": "Intégrité du classement",
                "content": (
                    "Toute tentative de manipulation du classement est strictement interdite : "
                    "création de plusieurs comptes, utilisation de scripts automatisés, partage de réponses pour gonfler un score, "
                    "ou toute autre forme de triche. "
                    "Tout compte en infraction pourra être supprimé immédiatement et sans préavis, "
                    "sans recours possible auprès de l'éditeur."
                ),
            },
            {
                "title": "Propriété intellectuelle",
                "content": (
                    "Les problèmes, énoncés et solutions rédigés par l'équipe éditoriale sont mis à disposition "
                    "sous licence Creative Commons CC BY-NC-SA 4.0. "
                    "Vous pouvez les utiliser et les partager à condition de citer braincollider.fr comme source, "
                    "de ne pas en faire un usage commercial, et de redistribuer sous la même licence. "
                    "Toute reproduction à des fins commerciales est interdite sans autorisation écrite préalable."
                ),
            },
            {
                "title": "Responsabilité",
                "content": (
                    "Braincollider est une plateforme éducative bénévole. Les contenus sont fournis à titre indicatif "
                    "et peuvent comporter des erreurs. L'éditeur ne saurait être tenu responsable d'un préjudice "
                    "lié à l'utilisation des ressources du site dans un cadre concours ou académique. "
                    "Le site est fourni 'en l'état', sans garantie de disponibilité continue."
                ),
            },
            {
                "title": "Modification des CGU",
                "content": (
                    "L'éditeur se réserve le droit de modifier les présentes CGU à tout moment. "
                    "Les utilisateurs disposant d'un compte seront informés par e-mail de toute modification substantielle. "
                    "La poursuite de l'utilisation du site après modification vaut acceptation des nouvelles CGU."
                ),
            },
            {
                "title": "Droit applicable",
                "content": (
                    "Les présentes CGU sont soumises au droit français. "
                    "En cas de litige, une solution amiable sera recherchée en priorité via contact@braincollider.fr. "
                    "À défaut, les tribunaux compétents seront saisis."
                ),
            },
        ],
    )