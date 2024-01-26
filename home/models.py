from django.db import models


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100, default="")
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


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
    email = models.EmailField(max_length=255, unique=True, null=False)
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

    contract_equipments = models.ManyToManyField("Person", through="ContractEquipment")

    def __str__(self):
        return self.first_name + " " + self.last_name

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


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    installation_date = models.DateField(null=False)
    monthly_charges = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    billing_date = models.DateField(null=False)
    renewal_date = models.DateField(null=False)
    person = models.ForeignKey("Person", on_delete=models.CASCADE, null=False)
    role = models.CharField(max_length=255, null=False)

    contract_equipments = models.ManyToManyField(
        "Equipment", through="ContractEquipment"
    )

    def __str__(self):
        return str(self.installation_date)

    def to_dict(self):
        return {
            "id": self.id,
            "installation_date": self.installation_date.isoformat()
            if self.installation_date
            else None,
            "monthly_charges": str(self.monthly_charges),
            "billing_date": self.billing_date.isoformat()
            if self.billing_date
            else None,
            "renewal_date": self.renewal_date.isoformat()
            if self.renewal_date
            else None,
            "person_id": self.person_id,
            "role": self.role,
        }

    class Meta:
        db_table = "contracts"


class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    asset_tag_number = models.CharField(max_length=255, unique=True, null=False)
    equipment_name = models.CharField(max_length=255, null=False)
    serial_number = models.CharField(max_length=255, unique=True, null=False)
    install_date = models.DateField(null=False)

    business = models.ForeignKey(
        "Business", on_delete=models.CASCADE, null=True, blank=True
    )

    contract_equipments = models.ManyToManyField(
        "Contract", through="ContractEquipment"
    )

    def __str__(self):
        return self.asset_tag_number

    def to_dict(self):
        return {
            "id": self.id,
            "asset_tag_number": self.asset_tag_number,
            "equipment_name": self.equipment_name,
            "serial_number": self.serial_number,
            "install_date": self.install_date.isoformat()
            if self.install_date
            else None,
        }

    class Meta:
        db_table = "equipments"


class ContractEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey("Contract", on_delete=models.CASCADE)
    equipment = models.ForeignKey("Equipment", on_delete=models.CASCADE)
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, null=True, blank=True
    )

    def __int__(self):
        return self.id

    def to_dict(self):
        return {
            "contract_id": self.contract.id,
            "equipment_id": self.equipment.id,
            "person_id": self.person.id if self.person else None,
        }

    class Meta:
        db_table = "contract_equipments"
        unique_together = (("contract", "equipment"),)


class Business(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "business"


from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        OWNER = "OWNER", "Owner"
        STAFF = "STAFF", "Staff"

    # base_role = Role.ADMIN

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


class OwnerManager(models.Manager):
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


class StaffManager(models.Manager):
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
