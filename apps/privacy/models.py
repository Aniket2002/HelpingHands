from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from cryptography.fernet import Fernet
import json
import uuid

User = get_user_model()

class PrivacySettings(models.Model):
    """User privacy settings and preferences"""
    VISIBILITY_CHOICES = [
        ('private', 'Private - Only me'),
        ('therapist', 'Therapist only'),
        ('friends', 'Friends only'),
        ('public', 'Public'),
    ]
    
    DATA_RETENTION_CHOICES = [
        (30, '30 days'),
        (90, '90 days'),
        (365, '1 year'),
        (1095, '3 years'),
        (-1, 'Indefinitely'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='privacy_settings')
    
    # Profile visibility
    profile_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    mood_data_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='therapist')
    journal_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    activity_visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Data retention
    mood_data_retention = models.IntegerField(choices=DATA_RETENTION_CHOICES, default=365)
    journal_data_retention = models.IntegerField(choices=DATA_RETENTION_CHOICES, default=1095)
    chat_data_retention = models.IntegerField(choices=DATA_RETENTION_CHOICES, default=90)
    
    # Communication preferences
    allow_therapist_messages = models.BooleanField(default=True)
    allow_peer_messages = models.BooleanField(default=False)
    allow_group_invitations = models.BooleanField(default=True)
    allow_research_participation = models.BooleanField(default=False)
    
    # Security settings
    two_factor_enabled = models.BooleanField(default=False)
    login_notifications = models.BooleanField(default=True)
    data_export_notifications = models.BooleanField(default=True)
    
    # Consent tracking
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)
    hipaa_authorization_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Privacy Settings for {self.user.get_full_name()}"

class DataEncryption(models.Model):
    """Manage encryption keys for sensitive data"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='encryption_keys')
    encryption_key = models.TextField()  # Encrypted with master key
    salt = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def generate_key_for_user(cls, user):
        """Generate and store encryption key for user"""
        key = Fernet.generate_key()
        # In production, encrypt this key with a master key
        return cls.objects.create(
            user=user,
            encryption_key=key.decode(),
            salt=str(uuid.uuid4())
        )
    
    def get_fernet(self):
        """Get Fernet instance for encryption/decryption"""
        return Fernet(self.encryption_key.encode())

class AccessLog(models.Model):
    """Log all access to sensitive user data"""
    ACTION_TYPES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('share', 'Share'),
    ]
    
    RESOURCE_TYPES = [
        ('mood_entry', 'Mood Entry'),
        ('journal_entry', 'Journal Entry'),
        ('chat_message', 'Chat Message'),
        ('appointment', 'Appointment'),
        ('therapy_notes', 'Therapy Notes'),
        ('assessment', 'Assessment'),
        ('profile', 'Profile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    accessor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='accesses_made')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    resource_id = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.accessor} {self.action_type} {self.resource_type} for {self.user}"

class DataExportRequest(models.Model):
    """GDPR/HIPAA data export requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    data_types = models.JSONField(default=list)  # List of data types to export
    file_format = models.CharField(max_length=10, choices=[('json', 'JSON'), ('csv', 'CSV')], default='json')
    file_path = models.CharField(max_length=500, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    download_token = models.CharField(max_length=64, blank=True)
    download_expires_at = models.DateTimeField(null=True, blank=True)
    downloaded_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Data Export for {self.user.get_full_name()} - {self.status}"

class DataDeletionRequest(models.Model):
    """GDPR right to be forgotten requests"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('denied', 'Denied'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deletion_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(max_length=1000)
    data_types = models.JSONField(default=list)  # Specific data types to delete
    retention_override = models.BooleanField(default=False)  # Override retention policy
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_deletions')
    review_notes = models.TextField(blank=True)
    scheduled_deletion_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Deletion Request for {self.user.get_full_name()} - {self.status}"

class ConsentLog(models.Model):
    """Track user consent for various purposes"""
    CONSENT_TYPES = [
        ('terms_of_service', 'Terms of Service'),
        ('privacy_policy', 'Privacy Policy'),
        ('hipaa_authorization', 'HIPAA Authorization'),
        ('data_processing', 'Data Processing'),
        ('marketing', 'Marketing Communications'),
        ('research', 'Research Participation'),
        ('data_sharing', 'Data Sharing'),
        ('cookies', 'Cookie Usage'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='consent_logs')
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPES)
    granted = models.BooleanField()
    version = models.CharField(max_length=20)  # Version of policy/terms
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    evidence = models.JSONField(default=dict)  # Additional evidence (e.g., checkbox states)
    timestamp = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'consent_type', '-timestamp']),
        ]
    
    def __str__(self):
        status = "Granted" if self.granted else "Revoked"
        consent_display = dict(self.CONSENT_TYPES).get(self.consent_type, self.consent_type)
        return f"{self.user.get_full_name()} {status} {consent_display}"

class SecurityIncident(models.Model):
    """Track security incidents and breaches"""
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    INCIDENT_TYPES = [
        ('unauthorized_access', 'Unauthorized Access'),
        ('data_breach', 'Data Breach'),
        ('suspicious_login', 'Suspicious Login'),
        ('malware', 'Malware Detection'),
        ('phishing', 'Phishing Attempt'),
        ('ddos', 'DDoS Attack'),
        ('insider_threat', 'Insider Threat'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('contained', 'Contained'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Affected data
    affected_users = models.ManyToManyField(User, blank=True, related_name='security_incidents')
    data_types_affected = models.JSONField(default=list)
    estimated_records_affected = models.PositiveIntegerField(null=True, blank=True)
    
    # Investigation
    detected_at = models.DateTimeField()
    reported_at = models.DateTimeField(auto_now_add=True)
    investigated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='investigated_incidents')
    containment_actions = models.TextField(blank=True)
    resolution_actions = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    
    # Legal/Compliance
    authorities_notified = models.BooleanField(default=False)
    users_notified = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    regulatory_filing_required = models.BooleanField(default=False)
    
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-detected_at']
    
    def __str__(self):
        severity_display = dict(self.SEVERITY_LEVELS).get(self.severity, self.severity)
        return f"{self.title} - {severity_display}"

class ComplianceAudit(models.Model):
    """HIPAA compliance audit logs"""
    AUDIT_TYPES = [
        ('access_controls', 'Access Controls'),
        ('data_encryption', 'Data Encryption'),
        ('backup_recovery', 'Backup & Recovery'),
        ('user_training', 'User Training'),
        ('risk_assessment', 'Risk Assessment'),
        ('incident_response', 'Incident Response'),
        ('data_retention', 'Data Retention'),
    ]
    
    STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('partial', 'Partially Compliant'),
        ('pending', 'Pending Review'),
    ]
    
    audit_type = models.CharField(max_length=30, choices=AUDIT_TYPES)
    audit_date = models.DateField()
    auditor = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    findings = models.TextField()
    recommendations = models.TextField(blank=True)
    corrective_actions = models.TextField(blank=True)
    next_audit_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-audit_date']
    
    def __str__(self):
        audit_display = dict(self.AUDIT_TYPES).get(self.audit_type, self.audit_type)
        return f"{audit_display} Audit - {self.audit_date}"
