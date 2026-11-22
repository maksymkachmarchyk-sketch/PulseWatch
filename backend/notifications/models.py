from django.db import models
# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    incident = models.ForeignKey(
        'incidents.Incident',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    channel = models.CharField(max_length=20)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'pulsewatch_notifications'

    def __str__(self):
        return f'{self.channel} - {self.user}'