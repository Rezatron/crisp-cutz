# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('PlaygroundCustomuser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class PlaygroundAppointment(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_time = models.DateTimeField()
    user = models.ForeignKey('PlaygroundCustomuser', models.DO_NOTHING)
    barber = models.ForeignKey('PlaygroundBarber', models.DO_NOTHING)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playground_appointment'


class PlaygroundAppointmentservice(models.Model):
    id = models.BigAutoField(primary_key=True)
    quantity = models.IntegerField()
    appointment = models.ForeignKey(PlaygroundAppointment, models.DO_NOTHING)
    service = models.ForeignKey('PlaygroundService', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_appointmentservice'


class PlaygroundAvailability(models.Model):
    id = models.BigAutoField(primary_key=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField()
    barber = models.ForeignKey('PlaygroundBarber', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_availability'


class PlaygroundBarber(models.Model):
    customuser_ptr = models.OneToOneField('PlaygroundCustomuser', models.DO_NOTHING, primary_key=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.CharField(max_length=100, blank=True, null=True)
    experience_years = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField()
    service_menu = models.TextField(blank=True, null=True)
    booking_preferences = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    specialization = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playground_barber'


class PlaygroundBarberservice(models.Model):
    id = models.BigAutoField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    barber = models.ForeignKey(PlaygroundBarber, models.DO_NOTHING)
    service = models.ForeignKey('PlaygroundService', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_barberservice'
        unique_together = (('barber', 'service'),)


class PlaygroundCustomer(models.Model):
    customuser_ptr = models.OneToOneField('PlaygroundCustomuser', models.DO_NOTHING, primary_key=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    notification_preferences = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playground_customer'


class PlaygroundCustomerCustomerGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(PlaygroundCustomer, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_customer_customer_groups'
        unique_together = (('customer', 'group'),)


class PlaygroundCustomuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'playground_customuser'


class PlaygroundCustomuserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(PlaygroundCustomuser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_customuser_groups'
        unique_together = (('customuser', 'group'),)


class PlaygroundCustomuserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(PlaygroundCustomuser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_customuser_user_permissions'
        unique_together = (('customuser', 'permission'),)


class PlaygroundReview(models.Model):
    id = models.BigAutoField(primary_key=True)
    stars = models.IntegerField()
    service_type = models.CharField(max_length=100)
    review_text = models.TextField(blank=True, null=True)
    user = models.ForeignKey(PlaygroundCustomuser, models.DO_NOTHING)
    barber = models.ForeignKey(PlaygroundBarber, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'playground_review'


class PlaygroundService(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()

    class Meta:
        managed = False
        db_table = 'playground_service'
