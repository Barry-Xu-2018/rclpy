# Copyright 2023 Sony Group Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import weakref

import rclpy
from rcl_interfaces.msg import LoggerLevel, SetLoggerLevelsResult
from rcl_interfaces.srv import GetLoggerLevels
from rcl_interfaces.srv import SetLoggerLevels
from rclpy.qos import qos_profile_services_default
from rclpy.validate_topic_name import TOPIC_SEPARATOR_STRING

class LoggingService:

    def __init__(self, node):
        self._node_weak_ref = weakref.ref(node)
        node_name = node.get_name()

        get_logger_name_service_name = \
            TOPIC_SEPARATOR_STRING.join((node_name, 'get_logger_levels'))
        node.create_service(
            GetLoggerLevels, get_logger_name_service_name,
            self._get_logger_levels, qos_profile=qos_profile_services_default
        )

        set_logger_name_service_name = \
            TOPIC_SEPARATOR_STRING.join((node_name, 'set_logger_levels'))
        node.create_service(
            SetLoggerLevels, set_logger_name_service_name,
            self._set_logger_levels, qos_profile=qos_profile_services_default
        )

    def _get_logger_levels(self, request: GetLoggerLevels.Request, response: GetLoggerLevels.Response):
        for name in request.names :
            level = LoggerLevel()
            level.name = name
            try:
                l = rclpy.logging.get_logger_level(name)
            except RuntimeError:
                print('Error')
                l = 0
            level.level = l
            response.levels.append(level)
        return response


    def _set_logger_levels(self, request: SetLoggerLevels.Request, response: SetLoggerLevels.Response):
        for level in request.levels:
            result = SetLoggerLevelsResult()
            result.successful = True
            try:
                rclpy.logging.set_logger_level(level.name, level.level)
            except RuntimeError:
                result.successful = False
                result.reason = 'Failed to set logger level'
            response.results.append(result)
        return response

    def _get_node(self):
        node = self._node_weak_ref()
        if node is None:
            raise ReferenceError('Expected valid node weak reference')
        return node