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

from typing import Union

from ory.asyncio.async_pod import AsyncPod
from ory.ext.exceptions import PodAlreadyExistsException, PriorityAlreadyExistsException, PermissionException
from ory.states.permission import Permission


class AsyncPool:
    """
    A AsyncPool is the same as a Pool, but it is async.
    It is also used to group pods and a collection of pods.
    """
    def __init__(self, name: str, permission: Permission, priority: int = 0) -> None:
        self.__name = name.lower()
        self.__permission = permission
        self.__priority = priority

        self.__pods = dict()

    async def get_name(self) -> str:
        """
        It gets the name of the current pool.
        :return: The name of the pool
        """

        return self.__name

    async def get_permission(self) -> Permission:
        """
        It gets the permission of the current pool.
        :return: The Permission of the pool
        """

        return self.__permission

    async def get_priority(self) -> int:
        """
        It gets the priority of the current pool.
        :return: The priority of the pool
        """

        return self.__priority

    async def register_pod(self, pod: AsyncPod, override: bool = False) -> None:
        """
        This function registers a pod to the pool.
        If the pod already exists, you can override it.
        :param pod: The pod to register
        :param override: True if the pod should override an existing pod
        :return: None
        """

        if await pod.get_name() in self.__pods and not override:
            raise PodAlreadyExistsException("Pod already registered")

        for registered_pod in self.__pods.values():
            if await pod.get_priority() == await registered_pod.get_priority() and await pod.get_priority() != 0:
                raise PriorityAlreadyExistsException("Priority already exists")

            if await pod.get_name() == await registered_pod.get_name():
                raise PodAlreadyExistsException("Name already registered")

        if override and self.__permission == Permission.READ_ONLY:
            raise PermissionException("This pool is read only")

        self.__pods[await pod.get_name()] = pod

    async def register_pods(self, pods: list[AsyncPod], override: bool = False) -> None:
        """
        This function registers multiple pods to the pool.
        If a pod already exists, you can override it.
        :param pods: The pods to register
        :param override: True if the pods should override an existing pod
        :return: None
        """

        for pod in pods:
            await self.register_pod(pod, override)

    async def unregister_pod(self, pod: AsyncPod) -> None:
        """
        This function unregisters a pod from the pool.
        :param pod: The pod to unregister
        :return: None
        """

        if await pod.get_name() not in self.__pods:
            raise PodAlreadyExistsException("Pod already registered")

        if self.__permission == Permission.READ_ONLY:
            raise PermissionException("This pool is read only")

        del self.__pods[await pod.get_name()]

    async def unregister_pods(self, pods: list[AsyncPod]) -> None:
        """
        This function unregisters multiple pods from the pool.
        :param pods: The pods to unregister
        :return: None
        """

        for pod in pods:
            await self.unregister_pod(pod)

    async def get_all_pods(self) -> list:
        """
        This function gets all pods of the pool.
        :return: All pods of the pool
        """

        return list(self.__pods.values())

    async def get_pod_by_name(self, name: str) -> Union[AsyncPod, None]:
        """
        This function gets a pod by its name.
        :param name: The name of the pod.
        :return: If the pod exists, it returns the pod. Otherwise, it returns None.
        """

        for pod in self.__pods.values():
            if await pod.get_name() == name.lower():
                return pod

        return None

    async def get_pod_by_priority(self, priority: int) -> Union[list[AsyncPod], AsyncPod, None]:
        """
        This function gets a pod by its priority.
        :param priority: The priority of the pod.
        :return: If the priority is zero, it returns all pods with the priority zero. Otherwise, it returns the pod with the given priority or None if it does not exist.
        """

        if priority == 0:
            return [pod for pod in self.__pods.values() if await pod.get_priority() == 0]

        for pod in self.__pods.values():
            if await pod.get_priority() == priority:
                return pod

        return None

    async def get_standard_pods(self) -> list[AsyncPod]:
        """
        This function gets all pods with the priority zero.
        :return: All pods with the priority zero
        """

        return [pod for pod in self.__pods.values() if await pod.get_priority() == 0]
