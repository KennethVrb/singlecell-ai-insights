from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Conversation, Message, Run, User


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ['created_at']
    fields = ['role', 'content', 'citations', 'created_at']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'run', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['run__name', 'run__run_id', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'conversation',
        'role',
        'content_preview',
        'created_at',
    ]
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'conversation__run__name']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content

    content_preview.short_description = 'Content'


admin.site.register(User, UserAdmin)
admin.site.register(Run)
