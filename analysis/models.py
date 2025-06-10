from django.db import models
from django.urls import reverse

from exams.models import Exam


class AnalysisResult(models.Model):
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    result_json = models.JSONField()
    algorithm_version = models.CharField(max_length=50)
    minimum_similarity_threshold = models.FloatField(default=0.3)
    suspicious_threshold = models.FloatField(default=0.7)

    class Meta:
        ordering = ['-timestamp']  # Newest first

    def __str__(self):
        return f"Analysis for {self.exam.title if self.exam else 'Unknown Exam'} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def get_absolute_url(self):
        return reverse('analysis:result_detail', args=[str(self.id)])