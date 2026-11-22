from django.db import models
from monitors.models import Monitor
# Create your models here.
class CheckResult(models.Model):
    monitor = models.ForeignKey(
        'monitors.Monitor',
        on_delete=models.CASCADE,
        related_name='checks'
    )
    status_code = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)
    is_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pulsewatch_checks'

    def __str__(self):
        return f'{self.monitor.name} - {self.checked_at}'