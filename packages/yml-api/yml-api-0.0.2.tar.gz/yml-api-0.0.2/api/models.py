from django.db import models


class Scope(models.Model):
    username = models.CharField(max_length=50, db_index=True)
    groupname = models.CharField(max_length=50, db_index=True)
    scopename = models.CharField(max_length=50, db_index=True)
    modelname = models.CharField(max_length=50, db_index=True)
    value = models.IntegerField('Value', db_index=True)

    def __str__(self):
        return '{}|{}|{}|{}|{}'.format(self.username, self.groupname, self.modelname, self.scopename, self.value)
