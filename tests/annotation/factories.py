import factory

from django.contrib.auth import models


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group

    name = factory.Faker("slug", locale="fr_FR")
