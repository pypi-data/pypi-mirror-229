#  Copyright 2023 Nyria
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Any

from ory.ext.exceptions import PermissionException
from ory.states.permission import Permission


class Pod:
    """
    A Pod is like a storage system.
    You can store any type of data in it, but the storage type
    must be the same for all stored data in the pod.
    """

    def __init__(self, name: str, storage: Any, permission: Permission, priority: int = 0) -> None:
        self.__name = name.lower()
        self.__storage = storage
        self.__permission = permission
        self.__priority = priority

    def get_name(self) -> str:
        """
        It gets the name of the current pod.
        :return: Name of the pod
        """

        return self.__name

    def get_storage(self) -> Any:
        """
        It gets the stored data of the current pod.
        :return: The pod storage data
        """

        return self.__storage

    def get_permission(self) -> Permission:
        """
        It gets the permission of the current pod.
        :return: Permission of the pod
        """

        return self.__permission

    def get_priority(self) -> int:
        """
        It gets the priority of the current pod.
        :return: The priority of the pod
        """

        return self.__priority

    def set_new_storage(self, storage: Any) -> None:
        """
        It overrides the current storage data with the new one.
        :param storage: The new storage data
        :return: None
        """

        if self.__permission != Permission.ALL:
            raise PermissionException("Cannot change instance of read only pod")

        self.__storage = storage

    def set_new_priority(self, priority: int) -> None:
        """
        It sets a new priority for the current pod.
        :param priority: The new priority
        :return: None
        """

        if self.__permission == Permission.READ_ONLY:
            raise PermissionException("Cannot change priority of read only pod")

        self.__priority = priority

    def set_new_name(self, name: str) -> None:
        """
        It sets the new the of the current pod.
        :param name: The new name
        :return: None
        """

        if self.__permission == Permission.READ_ONLY:
            raise PermissionException("Cannot change name of read only pod")

        self.__name = name
