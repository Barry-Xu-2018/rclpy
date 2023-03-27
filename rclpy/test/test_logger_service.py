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
import concurrent.futures

import unittest

from rcl_interfaces.msg import LoggerLevel, SetLoggerLevelsResult
from rcl_interfaces.srv import GetLoggerLevels
from rcl_interfaces.srv import SetLoggerLevels
import rclpy
import rclpy.context
from rclpy.executors import SingleThreadedExecutor


class TestLoggerService(unittest.TestCase):

    def setUp(self):
        self.context = rclpy.context.Context()
        rclpy.init(context=self.context)
        self.test_node_with_logger_service = rclpy.create_node(
            'test_node_with_logger_service_enabled',
            namespace='/rclpy',
            context=self.context,
            enable_logger_service = True)

        self.test_node = rclpy.create_node(
            'test_logger_service',
            namespace='/rclpy',
            context=self.context)

        exit_event = concurrent.futures.Future()

        self.executor1 = SingleThreadedExecutor(context=self.context)
        self.executor1.add_node(self.test_node_with_logger_service)


        self.executor2 = SingleThreadedExecutor(context=self.context)
        self.executor2.add_node(self.test_node)

    def tearDown(self):
        self.executor.shutdown()
        self.test_node.destroy_node()
        self.test_node_with_logger_service.destroy_node()
        rclpy.shutdown(context=self.context)

    def test_connect_get_logger_service(self):
        client = self.test_node.create_client(
            GetLoggerLevels,
            '/rclpy/test_node_with_logger_service_enabled/get_logger_levels')
        try:
            self.assertTrue(client.wait_for_service(2))
        finally:
            self.test_node.destroy_client(client)

    def test_connect_set_logger_service(self):
        client = self.test_node.create_client(
            SetLoggerLevels,
            '/rclpy/test_node_with_logger_service_enabled/set_logger_levels'
        )
        try:
            self.assertTrue(client.wait_for_service(2))
        finally:
            self.test_node.destroy_client(client)


if __name__ == '__main__':
    unittest.main()