from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse

from problems.models import Submission
from .models import Group, GroupMembership, GroupInvitation


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
        messages.error(request, "You are not a member of this group.")
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
def create_group(request):
    """Create a new group"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            messages.error(request, "Group name is required.")
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
        
        messages.success(request, f"Group '{name}' created successfully!")
        return redirect('groups:group_detail', group_id=group.id)
    
    return render(request, 'groups/create_group.html')


@login_required
def invite_user(request, group_id):
    """Invite a user to a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is admin
    if not group.is_admin(request.user):
        messages.error(request, "You don't have permission to invite users to this group.")
        return redirect('groups:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        
        if not username:
            messages.error(request, "Username is required.")
            return redirect('groups:invite_user', group_id=group.id)
        
        try:
            user_to_invite = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, f"User '{username}' not found.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Check if user is already a member
        if group.is_member(user_to_invite):
            messages.warning(request, f"User '{username}' is already a member of this group.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Check if invitation already exists
        if GroupInvitation.objects.filter(
            group=group, 
            invited_user=user_to_invite,
            accepted=False
        ).exists():
            messages.warning(request, f"User '{username}' already has a pending invitation.")
            return redirect('groups:invite_user', group_id=group.id)
        
        # Create invitation
        GroupInvitation.objects.create(
            group=group,
            invited_user=user_to_invite,
            invited_by=request.user
        )
        
                
        messages.success(request, f"Invitation sent to '{username}'!")
        return redirect('groups:invite_user', group_id=group.id)
    
    context = {
        'group': group,
    }
    return render(request, 'groups/invite_user.html', context)


@login_required
def accept_invitation(request, invitation_id):
    """Accept a group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    
    # Check if this invitation is for the logged-in user
    if invitation.invited_user != request.user:
        messages.error(request, "This invitation is not for you.")
        return redirect('groups:group_list')
    
    # Check if already accepted
    if invitation.accepted:
        messages.warning(request, "This invitation has already been accepted.")
        return redirect('groups:group_list')
    
    invitation.accept()
    messages.success(request, f"You've joined group '{invitation.group.name}'!")
    return redirect('groups:group_detail', group_id=invitation.group.id)


@login_required
def decline_invitation(request, invitation_id):
    """Decline a group invitation"""
    invitation = get_object_or_404(GroupInvitation, id=invitation_id)
    
    # Check if this invitation is for the logged-in user
    if invitation.invited_user != request.user:
        messages.error(request, "This invitation is not for you.")
        return redirect('groups:group_list')
    
    group_name = invitation.group.name
    invitation.delete()
    messages.info(request, f"You declined the invitation to join '{group_name}'.")
    return redirect('groups:group_list')


@login_required
def leave_group(request, group_id):
    """Leave a group"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is a member
    if not group.is_member(request.user):
        messages.error(request, "You are not a member of this group.")
        return redirect('groups:group_list')
    
    # Check if user is the creator
    if group.created_by == request.user and group.get_member_count() > 1:
        messages.error(request, "The group creator cannot leave while other members exist. Delete the group instead.")
        return redirect('groups:group_detail', group_id=group.id)
    
    # Remove user from group
    membership = GroupMembership.objects.get(group=group, user=request.user)
    membership.delete()
    
    # If no members left, delete the group
    if group.get_member_count() == 0:
        group.delete()
        messages.info(request, f"You left the group and it was deleted as it has no members.")
    else:
        messages.info(request, f"You left the group '{group.name}'.")
    
    return redirect('groups:group_list')


@login_required
def delete_group(request, group_id):
    """Delete a group (admin only)"""
    group = get_object_or_404(Group, id=group_id)
    
    # Check if user is the creator
    if group.created_by != request.user:
        messages.error(request, "Only the group creator can delete this group.")
        return redirect('groups:group_detail', group_id=group.id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"Group '{group_name}' has been deleted.")
        return redirect('groups:group_list')
    
    context = {
        'group': group,
    }
    return render(request, 'groups/delete_group.html', context)
