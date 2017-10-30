from django.db import models
from django.conf import settings
from django.utils.translation import pgettext_lazy


from jsonfield import JSONField
import hashlib
import logging

logger = logger.getLogger(__name__)


# Create your models here.
from .protections import Protection, AssignedProtection
from .signals import validate_success

_htest = hashlib.new(settings.KEY_HASH_ALGO))
_htest.update("test")

if MAX_HASH_SIZE > len(h.hexdigest()):
    raise Exception("MAX_HASH_SIZE too small to hold digest in hexadecimal")

class PublicKeyManager(models.Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# also for account recovery
class PublicKey(models.Model):
    id = models.BigAutoField(primary_key=True)
    # don't check for similarity as the hash check will reveal all clashes
    key = models.BinaryField(editable=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    note = models.TextField(max_length=400, null=False)
    # can only be retrieved by hash or if it is the user
    # every hash has to be unique
    # TODO: people could steal public keys and block people from using service
    # needs key to mediate if clashes happen
    # don't use as primary key as algorithms could change
    # DON'T allow users to change hash
    hash = models.CharField(max_length=settings.MAX_HASH_SIZE, unique=True, null=False, editable=False)
    # allow admins editing to solve conflicts
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False)
    class Meta:
        indexes = [
            models.Index(fields=['hash']),
            models.Index(fields=['user']),
        ]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_key = self.key

    def save(self, *args, **kwargs):
        if self.key and self.__original_key != self.key:
            h = hashlib.new(settings.KEY_HASH_ALGO))
            h.update(self.key)
            self.hash = h.hexdigest()

        super().save(*args, **kwargs)


class UserComponent(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.SlugField(max_length=50, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    #data for requester (NOT FOR PROTECTION)
    data = JSONField(default={}, null=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    # should be used for retrieving active protections, related_name
    assigned = None
    protections = models.ManyToManyField(Protection, through=AssignedProtection, limit_choices_to=Protection.objects.valid())
    class Meta:
        unique_together = [("user", "name"),]
        indexes = [
            models.Index(fields=['user', 'name']),
        ]

    def validate(self, request):
        # with deny and protections
        if self.assigned.filter(code="deny").exists() and len(self.assigned) > 1:
            for p in self.assigned.exclude(code="deny"):
                if not p.validate(request):
                    return False
            for rec, error in validate_success.send_robust(sender=self.__class__, name=self.name, code="deny"):
                logger.error(error)
            return True
        else:
            # normally just one must be fullfilled (or)
            for p in self.assigned.all():
                if p.validate(request):
                    for rec, error in validate_success.send_robust(sender=self.__class__, name=self.name, code=p.code)
                        logger.error(error)
                    return True
            return False
