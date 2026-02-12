from django.db import models

class TravelProject(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Place(models.Model):
    project = models.ForeignKey(TravelProject, related_name='places', on_delete=models.CASCADE)
    external_id = models.IntegerField()
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    visited = models.BooleanField(default=False)

    class Meta:
        unique_together = ('project', 'external_id')

    def __str__(self):
        return f"{self.name} ({self.project.name})"
