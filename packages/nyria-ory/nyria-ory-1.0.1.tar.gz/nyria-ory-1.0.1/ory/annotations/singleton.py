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

from functools import wraps
from typing import Callable


def singleton(cls: Callable) -> Callable:
    """
    Decorate any class with this singleton func to make it as singleton class
    :param cls: The class to decorate
    :return: The singleton
    """

    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs) -> cls:
        """
        Get the instance of the singleton
        :param args: The arguments
        :param kwargs: The keyword arguments
        :return: The instance
        """

        instance = instances.setdefault(cls, cls(*args, **kwargs))
        return instance

    return get_instance
