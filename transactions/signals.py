from django.dispatch import receiver
from django.db.models.signals import post_save
from . import models


@receiver(post_save, sender=models.Transaction)
def calculate_user_balance(sender, instance, created, **kwargs):
    if created:
        if instance.type == 'income':
            instance.user.balance += instance.amount
            
        else:
            instance.user.balance -= instance.amount

        instance.user.save()
