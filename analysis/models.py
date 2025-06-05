from django.db import models
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
    
    def __str__(self):
        return f"Analysis for {self.exam.title} at {self.timestamp}"
