from django.shortcuts import render
from django.contrib.auth.models import User
from problems.models import Submission,Problem

def leaderboard(request):
    # On récupère tous les utilisateurs
    users = User.objects.all()

    leaderboard_data = []

    for user in users:
        # On récupère les soumissions correctes de cet utilisateur
        correct_submissions = Submission.objects.filter(user=user, is_correct=True)
        # Calcul du score total : somme des difficultés des problèmes réussis
        total_score = sum(sub.problem.difficulty for sub in correct_submissions)

        # On compte aussi le nombre de problèmes réussis
        solved_count = correct_submissions.count()

        leaderboard_data.append({
            'user': user,
            'total_score': total_score,
            'solved_count': solved_count,
        })

    # Tri décroissant par score
    leaderboard_data.sort(key=lambda x: x['total_score'], reverse=True)

    return render(request, 'leaderboard/leaderboard.html', {'leaderboard': leaderboard_data})
