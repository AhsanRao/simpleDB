from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager
import datetime


class Person(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    class Role(models.TextChoices):
        ADMINISTRATOR = "ADMIN", "Administrator"
        CLIENT = "CLIENT", "Client"
        EXECUTIVE = "EXEC", "Executive"
        LEGAL = "LEGAL", "Legal"
        ACCOUNTANT = "ACCT", "Accountant"

    id = models.AutoField(primary_key=True)
    # Person fields
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    gender = models.CharField(max_length=1, choices=Gender.choices, null=False)
    email = models.EmailField(max_length=255, null=False)
    role = models.CharField(max_length=255, null=False, choices=Role.choices)

    # Address fields
    street = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    state = models.CharField(max_length=255, null=False)
    zipcode = models.CharField(max_length=255, null=False)
    country = models.CharField(max_length=255, null=False)

    # Phone number fields
    home_phone_number = models.CharField(max_length=255, blank=True, null=True)
    business_phone_number = models.CharField(max_length=255, blank=True, null=True)

    business = models.ForeignKey(
        "Business", on_delete=models.CASCADE, null=True, blank=True
    )

    sale_items = models.ManyToManyField("Person", through="SaleItem")

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender,
            "email": self.email,
            "role": self.role,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zipcode": self.zipcode,
            "country": self.country,
            "home_phone_number": self.home_phone_number,
            "business_phone_number": self.business_phone_number,
        }

    class Meta:
        db_table = "persons"

        constraints = [
            models.UniqueConstraint(
                fields=["email", "business"], name="unique_email_per_business"
            )
        ]


class Sale(models.Model):
    PURCHASE_CHOICES = [
        ("One-Time", "One-Time"),
        ("Recurring", "Recurring"),
    ]

    PAYMENT_INTERVALS = [
        ("Monthly", "Monthly"),
        ("Quarterly", "Quarterly"),
        ("Half-Yearly", "Half-Yearly"),
        ("Yearly", "Yearly"),
        ("Manual", "Manual"),
    ]
    id = models.AutoField(primary_key=True)
    purchase_date = models.DateField(null=False, default=datetime.date.today)
    charges = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    payment_method = models.CharField(
        max_length=20, choices=PURCHASE_CHOICES, default="One-Time"
    )
    payment_interval = models.CharField(
        max_length=20, choices=PAYMENT_INTERVALS, null=True, blank=True
    )
    # renewal_date = models.DateField(null=True, blank=True)
    billing_date = models.DateField(null=True, blank=True)
    person = models.ForeignKey("Person", on_delete=models.CASCADE, null=False)
    role = models.CharField(max_length=255, null=False)

    sale_items = models.ManyToManyField("Item", through="SaleItem")

    business = models.ForeignKey(
        "Business", on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"{self.person} - {self.purchase_date}"

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_date": self.purchase_date.isoformat(),
            "charges": str(self.charges),
            "payment_method": self.payment_method,
            "payment_interval": self.payment_interval,
            "billing_date": self.billing_date.isoformat()
            if self.billing_date
            else None,
            "person_id": self.person_id,
            "role": self.role,
        }

    class Meta:
        db_table = "sales"


class Item(models.Model):
    id = models.AutoField(primary_key=True)
    asset_tag_number = models.CharField(max_length=255, null=False)
    item_name = models.CharField(max_length=255, null=False)
    serial_number = models.CharField(max_length=255, null=False)
    install_date = models.DateField(null=False)

    business = models.ForeignKey(
        "Business", on_delete=models.CASCADE, null=True, blank=True
    )

    sale_items = models.ManyToManyField("Sale", through="SaleItem")

    def __str__(self):
        return self.asset_tag_number

    def to_dict(self):
        return {
            "id": self.id,
            "asset_tag_number": self.asset_tag_number,
            "item_name": self.item_name,
            "serial_number": self.serial_number,
            "install_date": self.install_date.isoformat()
            if self.install_date
            else None,
        }

    class Meta:
        db_table = "items"
        constraints = [
            models.UniqueConstraint(
                fields=["asset_tag_number", "business"],
                name="unique_asset_tag_per_business",
            ),
            models.UniqueConstraint(
                fields=["serial_number", "business"],
                name="unique_serial_number_per_business",
            ),
        ]


class SaleItem(models.Model):
    id = models.AutoField(primary_key=True)
    sale = models.ForeignKey("Sale", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, null=True, blank=True
    )

    def __int__(self):
        return self.id

    def to_dict(self):
        return {
            "sale_id": self.sale.id,
            "item_id": self.item.id,
            "person_id": self.person.id if self.person else None,
        }

    class Meta:
        db_table = "sale_items"
        unique_together = (("sale", "item"),)


class Business(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "business"


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        OWNER = "OWNER", "Owner"
        STAFF = "STAFF", "Staff"

    # base_role = Role.ADMIN
    objects = UserManager()

    role = models.CharField(max_length=10, choices=Role.choices, null=False)
    # business_name = models.CharField(max_length=255, null=False, blank=True)
    email = models.EmailField(unique=True, null=False, blank=False)
    business = models.ForeignKey(
        "Business", on_delete=models.CASCADE, null=True, blank=True
    )

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )


class OwnerManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.OWNER)


class Owner(User):
    base_role = User.Role.OWNER
    objects = OwnerManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Welcome Owner!"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class StaffManager(UserManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(role=User.Role.STAFF)


class Staff(User):
    base_role = User.Role.STAFF
    objects = StaffManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Welcome Staff!"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)
