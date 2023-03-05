from django.contrib.auth.models import (
    Group,
    Permission
)


def get_groups():
    management_group, created = Group.objects.get_or_create(
        name="Management team"
    )
    Group.objects.get_or_create(name="Sales team")
    Group.objects.get_or_create(name="Support team")

    management_group.permissions.add(
        Permission.objects.get(
            name='Can add permission'
            )
        )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can change permission'
            )
        )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can delete permission'
            )
        )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can view permission'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can add user'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can change user'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can delete user'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can view user'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can add client'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can change client'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can delete client'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can view client'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can add contract'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can change contract'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can delete contract'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can view contract'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can add event'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can change event'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can delete event'
            )
    )
    management_group.permissions.add(
        Permission.objects.get(
            name='Can view event'
            )
    )
