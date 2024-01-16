from django.db import models

class Product(models.Model):
    id    = models.AutoField(primary_key=True)
    name  = models.CharField(max_length = 100) 
    info  = models.CharField(max_length = 100, default = '')
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Person(models.Model):
    class Gender(models.TextChoices):
        MALE = 'M', 'Male'
        FEMALE = 'F', 'Female'
        OTHER = 'O', 'Other'

    id          = models.AutoField(primary_key=True)
    # Person fields
    first_name  = models.CharField(max_length=255, null=False)
    last_name   = models.CharField(max_length=255, null=False)
    gender      = models.CharField(max_length=1, choices=Gender.choices, null=False)
    email       = models.EmailField(max_length=255, unique=True, null=False)
    role        = models.CharField(max_length=255, null=False)

    # Address fields
    street      = models.CharField(max_length=255, null=False)
    city        = models.CharField(max_length=255, null=False)
    state       = models.CharField(max_length=255, null=False)
    zipcode     = models.CharField(max_length=255, null=False)
    country     = models.CharField(max_length=255, null=False)

    # Phone number fields
    home_phone_number       = models.CharField(max_length=255, blank=True, null=True)
    business_phone_number   = models.CharField(max_length=255, blank=True, null=True)

    contract_equipments = models.ManyToManyField('Person', through='ContractEquipment')


    def __str__(self):
        return self.first_name + ' ' + self.last_name

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'gender': self.gender,
            'email': self.email,
            'role': self.role,
            'street': self.street,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'country': self.country,
            'home_phone_number': self.home_phone_number,
            'business_phone_number': self.business_phone_number,
        }

    class Meta:
        db_table = 'persons'


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    installation_date = models.DateField(null=False)
    monthly_charges = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    billing_date = models.DateField(null=False)
    renewal_date = models.DateField(null=False)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, null=False)
    role = models.CharField(max_length=255, null=False)

    contract_equipments = models.ManyToManyField('Equipment', through='ContractEquipment')

    def __str__(self):
        return str(self.installation_date)

    def to_dict(self):
        return {
            'id': self.id,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'monthly_charges': str(self.monthly_charges),
            'billing_date': self.billing_date.isoformat() if self.billing_date else None,
            'renewal_date': self.renewal_date.isoformat() if self.renewal_date else None,
            'person_id': self.person_id,
            'role': self.role
        }

    class Meta:
        db_table = 'contracts'

class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    asset_tag_number = models.CharField(max_length=255, unique=True, null=False)
    equipment_name = models.CharField(max_length=255, null=False)
    serial_number = models.CharField(max_length=255, unique=True, null=False)
    install_date = models.DateField(null=False)

    contract_equipments = models.ManyToManyField('Contract', through='ContractEquipment')

    def __str__(self):
        return self.asset_tag_number

    def to_dict(self):
        return {
            'id': self.id,
            'asset_tag_number': self.asset_tag_number,
            'equipment_name': self.equipment_name,
            'serial_number': self.serial_number,
            'install_date': self.install_date.isoformat() if self.install_date else None
        }

    class Meta:
        db_table = 'equipments'


class ContractEquipment(models.Model):
    id = models.AutoField(primary_key=True)
    contract = models.ForeignKey('Contract', on_delete=models.CASCADE)
    equipment = models.ForeignKey('Equipment', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True)

    def __int__(self):
        return self.id

    def to_dict(self):
        return {
            'contract_id': self.contract.id,
            'equipment_id': self.equipment.id,
            'person_id': self.person.id if self.person else None
        }

    class Meta:
        db_table = 'contract_equipments'
        unique_together = (('contract', 'equipment'),)
