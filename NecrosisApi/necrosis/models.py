from django.contrib.auth.models import AbstractUser
from django.db.models import JSONField
from django.db import models


# Model to Store all user account information
class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('regular', 'Regular'),
        ('google', 'Google'),
        ('github', 'GitHub'),
    ]
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='regular')
    profile_picture_url = models.URLField(blank=True, null=True)
    theme_preference = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark')], default='light')
    social_id = models.CharField(max_length=255, blank=True, null=True)
    social_extra_data = JSONField(blank=True, null=True)
    # New fields for user profile
    contact = models.CharField(max_length=64, blank=True, null=True, help_text='User contact information (phone, etc.)')
    organisation = models.CharField(max_length=128, blank=True, null=True, help_text='User organisation or affiliation')

    def __str__(self):
        return self.username

# Create your models here.
class Image(models.Model):
    idx = models.CharField(max_length=10, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='uploads/images/')
    uploaded = models.DateTimeField(auto_now_add=True, null=True)


# Model to track each analysis batch a user submits
class AnalysisSession(models.Model):
    """
    Tracks each analysis batch a user submits.
    Attributes:
        user: ForeignKey to User who submitted the batch
        session_id: Unique session identifier
        created_at: Timestamp of session creation
        num_images: Number of images analyzed in this session
        notes: Optional notes for the session
        session_name: User-editable session name
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='analysis_sessions')
    session_id = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    num_images = models.PositiveIntegerField()
    notes = models.TextField(blank=True, null=True)
    session_name = models.CharField(max_length=128, blank=True, null=True, help_text="User-editable session name")

    def __str__(self):
        return f"Session {self.session_id} by {self.user.username}"

# Model to store individual image analysis results
class CassavaImage(models.Model):
    """
    Stores individual image analysis results.
    Attributes:
        session: ForeignKey to associated AnalysisSession
        original_image: Original uploaded image file
        processed_image: Processed image file (optional)
        image_name: Name of the image
        uploaded_at: Timestamp of upload
        total_lesions: Total lesions count
        necrosis_percentage: Percentage of necrosis
        confidence_score: Optional confidence score
        metadata: Additional metadata (JSON)
    """
    session = models.ForeignKey('AnalysisSession', on_delete=models.CASCADE, related_name='cassava_images')
    original_image = models.ImageField(upload_to='uploads/originals/')
    processed_image = models.ImageField(upload_to='uploads/processed/', blank=True, null=True)
    image_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    total_lesions = models.PositiveIntegerField()
    necrosis_percentage = models.FloatField()
    confidence_score = models.FloatField(blank=True, null=True)
    metadata = JSONField(blank=True, null=True)

    def __str__(self):
        return self.image_name

# Model to generate downloadable result summaries for analysis sessions
class AnalysisReport(models.Model):
    """
    Generates downloadable result summaries for analysis sessions.
    Attributes:
        session: One-to-one link to AnalysisSession
        report_file: The generated report file (CSV/JSON/PDF)
        generated_at: Timestamp when the report was generated
        file_format: File format type (CSV, JSON, PDF, etc.)
        checksum: Checksum for file verification
    """
    session = models.OneToOneField('AnalysisSession', on_delete=models.CASCADE, related_name='report')
    report_file = models.FileField(upload_to='reports/')
    generated_at = models.DateTimeField(auto_now_add=True)
    file_format = models.CharField(max_length=10)
    checksum = models.CharField(max_length=128)

    def __str__(self):
        return f"Report for Session {self.session.session_id}"

# Model to provide an audit trail of user actions
class UserActivityLog(models.Model):
    """
    Provides an audit trail of user actions.
    Attributes:
        user: ForeignKey to User who performed the action
        activity_type: Type of activity (login/upload/download/etc.)
        timestamp: When the activity occurred
        ip_address: IP address of the user
        device_info: Device information
        context_data: Additional context data (JSON)
    """
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='activity_logs')
    activity_type = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_info = models.CharField(max_length=255, blank=True, null=True)
    context_data = JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"

# Model to manage social login tokens
class OAuthToken(models.Model):
    """
    Manages social login tokens for OAuth providers.
    Attributes:
        user: ForeignKey to User who owns the token
        provider: OAuth provider (Google/GitHub)
        access_token: Access token string
        refresh_token: Optional refresh token
        expires_at: Expiration timestamp
        token_type: Type of the token
        scope: Scope permissions
    """
    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('github', 'GitHub'),
    ]
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='oauth_tokens')
    provider = models.CharField(max_length=10, choices=PROVIDER_CHOICES)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=512, blank=True, null=True)
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=32)
    scope = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.user.username} - {self.provider} token"
