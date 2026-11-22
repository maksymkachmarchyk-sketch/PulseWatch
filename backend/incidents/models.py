from django.db import models

# Create your models here.
class Incident(models.Model):
    monitor = models.ForeignKey(
        'monitors.Monitor',
        on_delete=models.CASCADE,
        related_name='incidents'
    )   
    started_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    reason = models.TextField(blank=True)

    class Meta:
        db_table = 'pulsewatch_incidents'

    def __str__(self):
        return f'{self.monitor.name} - {self.started_at}'