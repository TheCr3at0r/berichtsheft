from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Logbook(models.Model):
    student_name = models.CharField(max_length=100)
    start_year = models.IntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2050)],
        help_text="The year the apprenticeship begins.",
    )
    student_address = models.CharField(max_length=200, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    specialty = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    trainer_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.student_name} ({self.start_year})"


class Year(models.Model):
    logbook = models.ForeignKey(Logbook, on_delete=models.CASCADE, related_name="years")
    year_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )

    def __str__(self):
        return f"Year {self.year_number} of {self.logbook.student_name}"

    class Meta:
        ordering = ["year_number"]


class Week(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="weeks")
    week_number = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(53)],
    )

    def __str__(self):
        return f"Week {self.week_number} of Year {self.year.year_number}"

    class Meta:
        ordering = ["week_number"]


class Task(models.Model):
    class CategoryChoices(models.TextChoices):
        OPS = "OPS", "Operational"
        TRAIN = "TRAIN", "Training"
        VOCAT = "VOCAT", "Vocational School"

    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name="entries")
    category = models.CharField(max_length=5, choices=CategoryChoices.choices)
    name = models.CharField(max_length=200)
    hours = models.FloatField()

    class Meta:
        ordering = ["category", "name"]
        verbose_name = "task"
        verbose_name_plural = "tasks"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.name} ({self.hours}h)"
