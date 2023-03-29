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

from rcl_interfaces.msg import LoggerLevel, SetLoggerLevelsResult
from rcl_interfaces.srv import GetLoggerLevels
from rcl_interfaces.srv import SetLoggerLevels
import rclpy
from rclpy.impl.logging_severity import LoggingSeverity
from rclpy.qos import qos_profile_services_default
from rclpy.validate_topic_name import TOPIC_SEPARATOR_STRING

ERR_MSG_INVAILD_LOGGER_NAME = 'Logger name is invaild.'
ERR_MSG_INVAILD_LOGGER_LEVEL = 'Logger level is invaild.'
ERR_MSG_LOGGING_INTERNAL_ERROR = 'Logging system internal error.'


class LoggingService:

    def __init__(self, node):
        node_name = node.get_name()

        get_logger_name_service_name = \
            TOPIC_SEPARATOR_STRING.join((node_name, 'get_logger_levels'))
        node.create_service(
            GetLoggerLevels, get_logger_name_service_name,
            self.__get_logger_levels, qos_profile=qos_profile_services_default
        )

        set_logger_name_service_name = \
            TOPIC_SEPARATOR_STRING.join((node_name, 'set_logger_levels'))
        node.create_service(
            SetLoggerLevels, set_logger_name_service_name,
            self.__set_logger_levels, qos_profile=qos_profile_services_default
        )

    def __get_logger_levels(self, request: GetLoggerLevels.Request,
                            response: GetLoggerLevels.Response):
        for name in request.names:
            level = LoggerLevel()
            level.name = name
            try:
                ret_level = rclpy.logging.get_logger_level(name)
            except RuntimeError:
                ret_level = 0
            level.level = ret_level
            response.levels.append(level)
        return response

    def __set_logger_levels(self, request: SetLoggerLevels.Request,
                            response: SetLoggerLevels.Response):
        for level in request.levels:
            result = SetLoggerLevelsResult()
            result.successful = False

            if level.name.strip() != '':
                if LoggingSeverity.valid_logging_severity(level.level):
                    try:
                        rclpy.logging.set_logger_level(level.name, level.level)
                        result.successful = True
                    except RuntimeError:
                        result.reason = ERR_MSG_LOGGING_INTERNAL_ERROR
                else:
                    result.reason = ERR_MSG_INVAILD_LOGGER_LEVEL
            else:
                result.reason = ERR_MSG_INVAILD_LOGGER_NAME

            response.results.append(result)
        return response
