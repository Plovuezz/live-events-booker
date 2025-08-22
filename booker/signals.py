from django.db.models.signals import post_save
from django.dispatch import receiver
from booker.models import User, Band, BandInfo


@receiver(post_save, sender=Band)
def create_band_info(sender, instance, created, **kwargs):
    if created:
        BandInfo.objects.create(band=instance)