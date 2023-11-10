from app.models import Notification
def notifications(request):
    allnotifications = Notification.objects.all()
    return {'notifications': allnotifications}