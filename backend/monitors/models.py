from django.db import models
# Create your models here.
class Monitor(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name='monitors'
    )
    name = models.CharField(max_length=100)
    url = models.URLField()
    max_checks = models.PositiveIntegerField(default=5, null=True, blank=True)
    checks_count = models.PositiveIntegerField(default=0)
    interval = models.PositiveIntegerField(default=60)
    timeout = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pulsewatch_monitors'
        ordering = ['-created_at']

    def __str__(self):
        return self.name