from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_members(self):
        return User.objects.filter(groupmembership__group=self)

    def get_member_count(self):
        return self.groupmembership_set.count()

    def is_member(self, user):
        return self.groupmembership_set.filter(user=user).exists()

    def is_admin(self, user):
        return self.groupmembership_set.filter(user=user, role='admin').exists()

    def get_group_ranking(self):
        """Get ranking of group members based on their total scores"""
        from problems.models import Submission
        
        members = self.get_members()
        ranking_data = []

        for user in members:
            correct_submissions = user.submission_set.filter(is_correct=True)
            total_score = user.profile.get_total_score()
            solved_count = correct_submissions.count()

            ranking_data.append({
                'user': user,
                'total_score': total_score,
                'solved_count': solved_count,
            })

        # Sort by score descending
        ranking_data.sort(key=lambda x: x['total_score'], reverse=True)
        return ranking_data


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.role})"


class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invitations')
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_invitations')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_group_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('group', 'invited_user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Invitation to {self.invited_user.username} for {self.group.name}"

    def accept(self):
        """Accept the invitation and add user to group"""
        if not self.accepted:
            self.accepted = True
            self.accepted_at = timezone.now()
            self.save()
            
            # Create group membership
            GroupMembership.objects.get_or_create(
                group=self.group,
                user=self.invited_user,
                defaults={'role': 'member'}
            )
