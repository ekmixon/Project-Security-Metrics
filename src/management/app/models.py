import json
from typing import List

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.fields.related import ManyToManyField
from packageurl import PackageURL


class Package(models.Model):
    package_url = models.CharField(max_length=256, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return self.package_url

    @property
    def full_name(self):
        if purl := PackageURL.from_string(self.package_url):
            return (
                f"{purl.namespace}/{purl.name}"
                if purl.type in ["npm", "github"] and purl.namespace
                else purl.name
            )

        else:
            return None

    @property
    def full_name_version(self):
        purl = PackageURL.from_string(self.package_url)
        return f"{self.full_name}@{purl.version}" if purl.version else self.full_name

    class Meta:
        db_table = "package"
        ordering = ["package_url"]


class Metric(models.Model):
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    key = models.CharField(max_length=256)
    value = models.TextField(null=True, blank=True)
    properties = models.JSONField(null=True, blank=True, encoder=DjangoJSONEncoder)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return f"{self.package} / {self.key}"

    class Meta:
        db_table = "metric"
        ordering = ["key"]
        indexes = [models.Index(fields=["package", "key"])]
