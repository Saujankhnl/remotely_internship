from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q, Max, Count, Subquery, OuterRef
from django.utils import timezone

from .models import ChatRoom, Message
from internships.models import JobApplication


def _get_room_for_user(room_id, user):
    """Return the ChatRoom if user is a participant, else None."""
    try:
        room = ChatRoom.objects.select_related(
            'application__applicant',
            'application__job__company',
        ).get(id=room_id)
    except ChatRoom.DoesNotExist:
        return None
    if user in [room.application.applicant, room.application.job.company]:
        return room
    return None


@login_required
def chat_room(request, application_id):
    """Show / create a chat room for a specific job application."""
    application = get_object_or_404(
        JobApplication.objects.select_related('applicant', 'job__company', 'job__company__company_profile'),
        pk=application_id,
    )

    if request.user not in [application.applicant, application.job.company]:
        return HttpResponseForbidden("You don't have permission to access this chat.")

    room, _ = ChatRoom.objects.get_or_create(application=application)

    messages_qs = room.messages.select_related('sender').order_by('-created_at')[:50]
    chat_messages = list(reversed(messages_qs))

    # Mark unread messages as read
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    # Determine the other participant's display name
    if request.user == application.applicant:
        profile = getattr(application.job.company, 'company_profile', None)
        other_name = profile.company_name if profile and profile.company_name else application.job.company.username
    else:
        other_name = application.full_name

    return render(request, 'chat/chat_room.html', {
        'room': room,
        'application': application,
        'chat_messages': chat_messages,
        'other_name': other_name,
        'current_user_id': request.user.id,
    })


@login_required
def chat_list(request):
    """List all chat rooms for the current user."""
    user = request.user

    if user.user_type == 'company':
        rooms = ChatRoom.objects.filter(
            application__job__company=user,
        )
    else:
        rooms = ChatRoom.objects.filter(
            application__applicant=user,
        )

    rooms = rooms.select_related(
        'application__applicant',
        'application__job__company',
        'application__job__company__company_profile',
    ).annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
        ),
    ).order_by('-last_message_time')

    # Attach last message preview to each room
    last_msg_subquery = Message.objects.filter(
        room=OuterRef('pk'),
    ).order_by('-created_at').values('content')[:1]

    rooms = rooms.annotate(last_message_preview=Subquery(last_msg_subquery))

    room_list = []
    for room in rooms:
        if user.user_type == 'company':
            other_name = room.application.full_name
        else:
            profile = getattr(room.application.job.company, 'company_profile', None)
            other_name = profile.company_name if profile and profile.company_name else room.application.job.company.username

        room_list.append({
            'room': room,
            'other_name': other_name,
            'job_title': room.application.job.title,
            'last_message': room.last_message_preview or '',
            'last_time': room.last_message_time,
            'unread': room.unread_count,
            'application_id': room.application_id,
        })

    return render(request, 'chat/chat_list.html', {
        'room_list': room_list,
    })


@login_required
@require_POST
def send_message_ajax(request, room_id):
    """AJAX fallback – save a message and return JSON."""
    room = _get_room_for_user(room_id, request.user)
    if room is None:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    content = request.POST.get('message', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    msg = Message.objects.create(room=room, sender=request.user, content=content)
    return JsonResponse({
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender_id,
        'sender_name': msg.sender.username,
        'timestamp': msg.created_at.isoformat(),
    })


@login_required
def fetch_messages_ajax(request, room_id):
    """AJAX fallback – return recent messages as JSON."""
    room = _get_room_for_user(room_id, request.user)
    if room is None:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    after = request.GET.get('after')
    qs = room.messages.select_related('sender').order_by('created_at')
    if after:
        qs = qs.filter(created_at__gt=after)
    else:
        qs = qs.order_by('-created_at')[:50]
        qs = sorted(qs, key=lambda m: m.created_at)

    data = [
        {
            'id': m.id,
            'content': m.content,
            'sender_id': m.sender_id,
            'sender_name': m.sender.username,
            'timestamp': m.created_at.isoformat(),
            'is_read': m.is_read,
            'attachment': m.attachment.url if m.attachment else None,
        }
        for m in qs
    ]
    return JsonResponse({'messages': data})


@login_required
@require_POST
def upload_attachment(request, room_id):
    """Handle file upload for chat attachments."""
    room = _get_room_for_user(room_id, request.user)
    if room is None:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    file = request.FILES.get('file')
    if not file:
        return JsonResponse({'error': 'No file provided'}, status=400)

    content = request.POST.get('message', '') or file.name
    msg = Message.objects.create(
        room=room,
        sender=request.user,
        content=content,
        attachment=file,
    )
    return JsonResponse({
        'id': msg.id,
        'content': msg.content,
        'sender_id': msg.sender_id,
        'sender_name': msg.sender.username,
        'timestamp': msg.created_at.isoformat(),
        'attachment': msg.attachment.url,
    })
