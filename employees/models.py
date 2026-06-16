from django.conf import settings
from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models

from core.models import BaseModel


class Department(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True)
    head = models.ForeignKey(
        'employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='departments_headed',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
    )
    cost_centre_code = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ('name',)
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_deleted', 'name']),
        ]

    def __str__(self):
        return self.name


class Designation(BaseModel):
    name = models.CharField(max_length=150)
    level = models.CharField(max_length=10, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='designations',
    )
    grade = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ('name',)
        unique_together = ('name', 'department')

    def __str__(self):
        return self.name


class Employee(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('probation', 'Probation'),
    ]

    employee_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True,
        blank=True,
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    join_date = models.DateField(db_index=True)
    location = models.CharField(max_length=100, blank=True)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
    )
    bank_account = models.CharField(max_length=100, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    salary_structure_id = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to='employees/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'png'])],
    )

    class Meta:
        ordering = ('-join_date',)
        indexes = [
            models.Index(fields=['status', 'department']),
            models.Index(fields=['manager', 'status']),
            models.Index(fields=['is_deleted', 'status']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class WorkHistory(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='work_history_entries',
    )
    employer = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    reason_for_leaving = models.TextField(blank=True)
    is_internal = models.BooleanField(default=False)

    class Meta:
        ordering = ('-start_date',)
        verbose_name_plural = 'work histories'

    def __str__(self):
        return f"{self.employee.full_name} - {self.employer}"


class EmergencyContact(BaseModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
    )
    name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class EmployeeDocument(BaseModel):
    DOCUMENT_TYPES = [
        ('offer_letter', 'Offer Letter'),
        ('id_proof', 'ID Proof'),
        ('experience_certificate', 'Experience Certificate'),
        ('education_certificate', 'Education Certificate'),
        ('other', 'Other'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png', 'xlsx', 'csv'])],
    )
    expiry_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.title}"
