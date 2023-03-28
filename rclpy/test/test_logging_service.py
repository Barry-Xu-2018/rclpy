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

import threading
import time

import unittest

from rcl_interfaces.msg import LoggerLevel, SetLoggerLevelsResult
from rcl_interfaces.srv import GetLoggerLevels
from rcl_interfaces.srv import SetLoggerLevels
import rclpy
import rclpy.context
from rclpy.executors import SingleThreadedExecutor
from rclpy.task import Future


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

        self.executor1 = SingleThreadedExecutor(context=self.context)
        self.executor1.add_node(self.test_node_with_logger_service)
        self.executor2 = SingleThreadedExecutor(context=self.context)
        self.executor2.add_node(self.test_node)

        self.exit_flag = Future()

        def spin_until_task_done(executor, exit_flag):
            executor.spin_until_future_complete(exit_flag)

        self.thread = threading.Thread(target=spin_until_task_done, args=(self.executor1, self.exit_flag))
        self.thread.start()   

    def tearDown(self):
        self.exit_flag.set_result(True)
        self.thread.join()
        self.executor.shutdown()
        self.test_node.destroy_node()
        self.test_node_with_logger_service.destroy_node()
        rclpy.shutdown(context=self.context)

    def test_connect_get_logger_service(self):
        client = self.test_node.create_client(
            GetLoggerLevels,
            '/rclpy/test_node_with_logger_service_enabled/get_logger_levels')
        #self.executor.spin_until_future_complete(Future(), 2)
        try:
            self.assertTrue(client.wait_for_service(2))
        finally:
            self.test_node.destroy_client(client)

    def test_connect_set_logger_service(self):
        client = self.test_node.create_client(
            SetLoggerLevels,
            '/rclpy/test_node_with_logger_service_enabled/set_logger_levels'
        )
        #self.executor.spin_until_future_complete(Future(), 2)
        try:
            self.assertTrue(client.wait_for_service(2))
        finally:
            self.test_node.destroy_client(client)

    def test_get_logger_service(self):
        client = self.test_node.create_client(
            GetLoggerLevels,
            '/rclpy/test_node_with_logger_service_enabled/get_logger_levels')
        client.wait_for_service(2)
        request = GetLoggerLevels.Request()
        request.names=['rcl']
        future = client.call_async(GetLoggerLevels.Request())
        self.executor2.spin_once_until_future_complete(future, 5)
        self.assertTrue(future.result() is not None)
        print(future.result())

if __name__ == '__main__':
    unittest.main()