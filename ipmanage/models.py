from django.db import models

# Create your models here.

class nets(models.Model):
#存放当前定义的网段
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=400, null=True)

class ips(models.Model):
#存放 IP 使用情况
    id = models.AutoField(primary_key=True)
    ip_addr = models.CharField(max_length=40)
    seq = models.BigIntegerField()
    net = models.ForeignKey(nets, on_delete=models.CASCADE)
    person = models.CharField(max_length=50, null=True)
    #department = models.CharField(max_length=50, null=True)
    add_date = models.CharField(max_length=50, null=True)
    
