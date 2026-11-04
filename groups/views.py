from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from problems.models import Submission
from .models import Group, GroupMembership, GroupInvitation
from core.rate_limits import rate_limit


@login_required
def group_list(request):
    """List all groups the user is a member of"""
    groups = Group.objects.filter(groupmembership__user=request.user).distinct()
    pending_invitations = GroupInvitation.objects.filter(
        invited_user=request.user, 
        accepted=False
    )
    
    # Determine which of these groups the current user is admin of
    admin_group_ids = list(
        GroupMembership.objects.filter(group__in=groups, user=request.user, role='admin')
        .values_list('group_id', flat=True)
    )

    context = {
        'groups': groups,
        'pending_invitations': pending_invitations,
        'pending_count': pending_invitations.count(),
        'admin_group_ids': admin_group_ids,
    }
    return render(request, 'groups/group_list.html', context)


@login_required
def group_detail(request, group_id):
    """View group details, ranking, and members"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is a member
    if not group.is_member(request.user):
        messages.error(request, "Vous n’êtes pas membre de ce groupe.")
        return redirect('groups:group_list')
    
    ranking = group.get_group_ranking()
    members = group.get_members()
    is_admin = group.is_admin(request.user)
    # Precompute admin user ids for template checks
    admin_user_ids = list(group.groupmembership_set.filter(role='admin').values_list('user_id', flat=True))
    
    context = {
        'group': group,
        'ranking': ranking,
        'members': members,
        'is_admin': is_admin,
        'member_count': group.get_member_count(),
        'admin_user_ids': admin_user_ids,
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
@rate_limit("group-create", limit=5, period=60 * 60, methods={"POST"})
def create_group(request):
    """Create a new group"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Le nom du groupe est obligatoire.")
            return redirect('groups:create_group')
        
        # Create the group
        group = Group.objects.create(
            name=name,
            description=description,
            created_by=request.user
        )
        
        # Add creator as admin member
        GroupMembership.objects.create(
            group=group,
            user=request.user,
            role='admin'
        )
        
        messages.success(request, f"Le groupe « {name} » a été créé.")
        return redirect('groups:group_detail', group_id=group.id)
    
    return render(request, 'groups/create_group.html')


@login_required
@rate_limit("group-invite", limit=30, period=60 * 60, methods={"POST"})
def invite_user(request, group_id):
    """Invite a user to a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is admin
    if not group.is_admin(request.user):
        messages.error(request, "Vous n’avez pas l’autorisation d’inviter des membres dans ce groupe.")
        return redirect('groups:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        if not username:
            messages.error(request, "Le nom d’utilisateur est obligatoire.")
            return redirect('groups:invite_user', group_id=group.id)
        
        try:
            user_to_invite = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"L’utilisateur « {username} » est introuvable.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Check if user is already a member
        if group.is_member(user_to_invite):
            messages.warning(request, f"« {username} » est déjà membre de ce groupe.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Check if invitation already exists
        if GroupInvitation.objects.filter(
            group=group, 
            invited_user=user_to_invite,
            accepted=False
        ).exists():
            messages.warning(request, f"Une invitation pour « {username} » est déjà en attente.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Create invitation
        GroupInvitation.objects.create(
            group=group,
            invited_user=user_to_invite,
            invited_by=request.user
        )
        
                
        messages.success(request, f"L’invitation a été envoyée à « {username} ».")
        return redirect('groups:invite_user', group_id=group.id)
    
    context = {
        'group': group,
    }
    return render(request, 'groups/invite_user.html', context)


@login_required
@require_POST
def accept_invitation(request, invitation_id):
    """Accept a group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    
    # Check if this invitation is for the logged-in user
    if invitation.invited_user != request.user:
        messages.error(request, "Cette invitation ne vous est pas destinée.")
        return redirect('groups:group_list')
    
    # Check if already accepted
    if invitation.accepted:
        messages.warning(request, "Cette invitation a déjà été acceptée.")
        return redirect('groups:group_list')
    
    invitation.accept()
    messages.success(request, f"Vous avez rejoint le groupe « {invitation.group.name} ».")
    return redirect('groups:group_detail', group_id=invitation.group.id)


@login_required
@require_POST
def decline_invitation(request, invitation_id):
    """Decline a group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    
    # Check if this invitation is for the logged-in user
    if invitation.invited_user != request.user:
        messages.error(request, "Cette invitation ne vous est pas destinée.")
        return redirect('groups:group_list')
    
    group_name = invitation.group.name
    invitation.delete()
    messages.info(request, f"Vous avez refusé l’invitation au groupe « {group_name} ».")
    return redirect('groups:group_list')


@login_required
@require_POST
def leave_group(request, group_id):
    """Leave a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is a member
    if not group.is_member(request.user):
        messages.error(request, "Vous n’êtes pas membre de ce groupe.")
        return redirect('groups:group_list')
    
    # Check if user is the creator
    if group.created_by == request.user and group.get_member_count() > 1:
        messages.error(request, "Le créateur ne peut pas quitter le groupe tant qu’il reste d’autres membres. Vous pouvez supprimer le groupe.")
        return redirect('groups:group_detail', group_id=group.id)
    
    # Remove user from group
    membership = GroupMembership.objects.get(group=group, user=request.user)
    membership.delete()
    
    # If no members left, delete the group
    if group.get_member_count() == 0:
        group.delete()
        messages.info(request, "Vous avez quitté le groupe. Comme il n’avait plus de membres, il a été supprimé.")
    else:
        messages.info(request, f"Vous avez quitté le groupe « {group.name} ».")
    
    return redirect('groups:group_list')


@login_required
def delete_group(request, group_id):
    """Delete a group (admin only)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is the creator
    if group.created_by != request.user:
        messages.error(request, "Seul le créateur du groupe peut le supprimer.")
        return redirect('groups:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"Le groupe « {group_name} » a été supprimé.")
        return redirect('groups:group_list')
    
    context = {
        'group': group,
    }
    return render(request, 'groups/delete_group.html', context)
