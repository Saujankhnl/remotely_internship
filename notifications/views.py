from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required
def notification_list(request):
    notifications = (
        Notification.objects
        .filter(user=request.user)
        .select_related('user')
    )

    # Mark all unread as read
    notifications.filter(is_read=False).update(is_read=True)

    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'notifications/notification_list.html', {
        'page_obj': page_obj,
    })


@login_required
def notification_count_api(request):
    count = (
        Notification.objects
        .filter(user=request.user, is_read=False)
        .only('id')
        .count()
    )
    return JsonResponse({'unread_count': count})


@login_required
def notification_preview_api(request):
    notifications = (
        Notification.objects
        .filter(user=request.user, is_read=False)
        .only('id', 'message', 'notification_type', 'related_url', 'created_at')
        .order_by('-created_at')[:5]
    )
    data = [
        {
            'id': n.id,
            'message': n.message,
            'notification_type': n.notification_type,
            'related_url': n.related_url,
            'created_at': n.created_at.isoformat(),
        }
        for n in notifications
    ]
    return JsonResponse({'notifications': data})


@login_required
@require_POST
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})
