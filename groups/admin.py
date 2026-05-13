from django.contrib import admin
from .models import Group, GroupMembership, GroupInvitation


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'get_member_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_member_count(self, obj):
        return obj.get_member_count()
    get_member_count.short_description = 'Members'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)


@admin.register(GroupInvitation)
class GroupInvitationAdmin(admin.ModelAdmin):
    list_display = ('invited_user', 'group', 'invited_by', 'accepted', 'created_at')
    list_filter = ('accepted', 'created_at')
    search_fields = ('invited_user__username', 'group__name', 'invited_by__username')
    readonly_fields = ('created_at', 'accepted_at')
