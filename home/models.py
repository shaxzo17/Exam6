from django.db import models

# Create your models here.
class Konditsioner(models.Model):
    name = models.CharField(max_length=56)
    brand = models.CharField(max_length=25)
    color = models.CharField(max_length=20)
    number = models.IntegerField()
    image = models.ImageField(upload_to='kontitsionerlar/' , blank=True , null=True , default='default/cond.jpg')
    price = models.DecimalField(max_digits=12 , decimal_places=2)
    desc = models.CharField(max_length=200 , blank=True , null=True)

    def __str__(self):
        return self.name