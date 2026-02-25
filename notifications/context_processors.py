from django.core.cache import cache


def notification_count(request):
    if not request.user.is_authenticated:
        return {'unread_notification_count': 0}
    key = f'unread_notif:{request.user.id}'
    count = cache.get(key)
    if count is None:
        count = request.user.notifications.filter(is_read=False).count()
        cache.set(key, count, 60)
    return {'unread_notification_count': count}
