import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_srvs.srv import SetBool
from xarmclient import XArm


class GripperNode(Node):
    #creates node as gripper and adds a grip service
    def __init__(self):
        super().__init__("gripper_node")
        self.service = self.create_service(SetBool, "grip", self.service_callback)
        self.xarm = XArm()
        
    def service_callback(self, request, response):
        state = "closing" if request.data else "opening"
        response.success = True
        response.message = f"Gripper {state} executed"
        ##if closed open, if open close
        self.xarm.grip(request.data)

        return response

def main(args=None):
    try:
        with rclpy.init(args=args):
            node = GripperNode()
            rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

if __name__ == '__main__':
    main()