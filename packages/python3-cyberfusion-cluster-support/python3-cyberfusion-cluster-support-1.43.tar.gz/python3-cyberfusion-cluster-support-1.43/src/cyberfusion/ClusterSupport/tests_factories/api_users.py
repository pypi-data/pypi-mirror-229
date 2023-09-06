"""Factories for API object."""

import factory
import factory.fuzzy

from cyberfusion.ClusterSupport.api_users import APIUser
from cyberfusion.ClusterSupport.tests_factories import BaseBackendFactory


class APIUserFactory(BaseBackendFactory):
    """Factory for specific object."""

    class Meta:
        """Settings."""

        model = APIUser

    username = factory.Faker("user_name")
    is_active = factory.Faker("boolean")
    is_provisioning_user = factory.Faker("boolean")
    is_superuser = factory.Faker("boolean")
    trusted_ip_networks = None
    password = factory.Faker("password", length=24)
