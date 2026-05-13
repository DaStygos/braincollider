from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from problems.models import Problem, Submission
from .models import Group, GroupInvitation, GroupMembership

User = get_user_model()


class GroupsTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user1 = User.objects.create_user(username='alice', password='pass')
		self.user2 = User.objects.create_user(username='bob', password='pass')

	def test_create_group_and_invite_flow(self):
		# Login as alice and create a group
		self.client.login(username='alice', password='pass')
		create_url = reverse('groups:create_group')
		resp = self.client.post(create_url, {'name': 'Team A', 'description': 'Private group'})
		group = Group.objects.get(name='Team A')
		# Creator should be admin member
		self.assertTrue(GroupMembership.objects.filter(group=group, user=self.user1, role='admin').exists())

		# Invite bob
		invite_url = reverse('groups:invite_user', args=[group.id])
		resp = self.client.post(invite_url, {'username': 'bob'}, follow=True)
		invitation = GroupInvitation.objects.filter(group=group, invited_user=self.user2, accepted=False).first()
		self.assertIsNotNone(invitation)

		# Bob accepts invitation
		self.client.logout()
		self.client.login(username='bob', password='pass')
		accept_url = reverse('groups:accept_invitation', args=[invitation.id])
		resp = self.client.get(accept_url, follow=True)
		self.assertTrue(GroupMembership.objects.filter(group=group, user=self.user2).exists())

	def test_only_admin_can_invite(self):
		# Create group with alice
		self.client.login(username='alice', password='pass')
		resp = self.client.post(reverse('groups:create_group'), {'name': 'Team B'})
		group = Group.objects.get(name='Team B')
		self.client.logout()

		# Bob (not admin) cannot invite
		self.client.login(username='bob', password='pass')
		resp = self.client.post(reverse('groups:invite_user', args=[group.id]), {'username': 'alice'}, follow=True)
		self.assertFalse(GroupInvitation.objects.filter(group=group, invited_user=self.user1).exists())

	def test_group_ranking_reflects_submissions(self):
		# Create a problem and submissions for both users
		problem = Problem.objects.create(title='P1', statement='x', solution='y', difficulty=2)

		Submission.objects.create(user=self.user1, problem=problem, answer='ok', is_correct=True)
		Submission.objects.create(user=self.user2, problem=problem, answer='ok', is_correct=True)

		# Create group and add both members
		self.client.login(username='alice', password='pass')
		self.client.post(reverse('groups:create_group'), {'name': 'Team Rank'})
		group = Group.objects.get(name='Team Rank')
		GroupMembership.objects.create(group=group, user=self.user2, role='member')

		ranking = group.get_group_ranking()
		# Both users should appear and have equal score
		usernames = [e['user'].username for e in ranking]
		self.assertIn('alice', usernames)
		self.assertIn('bob', usernames)
		scores = {e['user'].username: e['total_score'] for e in ranking}
		self.assertEqual(scores['alice'], scores['bob'])
