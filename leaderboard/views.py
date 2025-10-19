from django.shortcuts import render
from django.contrib.auth.models import User

def leaderboard(request):
    users = User.objects.all()

    leaderboard_data = []

    for user in users:
        correct_submissions = user.profile.get_submissions().filter(is_correct=True)
        total_score = user.profile.get_total_score()
        solved_count = correct_submissions.count()

        leaderboard_data.append({
            'user': user,
            'total_score': total_score,
            'solved_count': solved_count,
        })

    # Tri décroissant par score et filtrage
    leaderboard_data.sort(key=lambda x: x['total_score'], reverse=True)
    leaderboard_data = list(filter(lambda x: x['total_score'] > 0, leaderboard_data))

    return render(request, 'leaderboard/leaderboard.html', {'leaderboard': leaderboard_data})
