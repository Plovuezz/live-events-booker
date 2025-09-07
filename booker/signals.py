from django.db.models.signals import post_save
from django.dispatch import receiver
from booker.models import Band, BandInfo

# I don't need this for now, because when I create a band through admin panel bandinfo creates and connects through inline (watch admin.py AdminBand)
# @receiver(post_save, sender=Band)
# def create_band_info(sender, instance, created, **kwargs):
#     if created:
#         BandInfo.objects.create(band=instance)
