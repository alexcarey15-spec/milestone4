import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import Trigger
from xarmclient import XArm

class HomingNode(Node):
    # create homing node and its service
    def __init__(self):
        super().__init__("homing_node")
        self.service = self.create_service(Trigger, "homing", self.service_callback)
        self.xarm = XArm()
        
    # listens to requests and logs when requested
    def service_callback(self, request, response):
        response.success = True
        response.message = "Homing"

        self.xarm.home()
        return response

def main(args=None):
    try:
        with rclpy.init(args=args):
            node = HomingNode()
            rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

if __name__ == '__main__':
    main()