import threading
import time
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.node import Node
from sensor_msgs.msg import JointState
from wx250s_interface.action import JointPTP
from xarmclient import XArm
import math
class JointPTPNode(Node):
    def __init__(self):
        super().__init__("joint_ptp_node")
        self.goal_handle = None
        self.goal_lock = threading.Lock()
        self.subscription = self.create_subscription(JointState, "joint_state", self.joint_state_callback,10)
        self.angles = [0.0] * 6## array of the joints
        
        
        self.action_server = ActionServer(
            self,
            JointPTP,
            'set_joint_ptp',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            handle_accepted_callback=self.handle_accepted_callback,
            cancel_callback=self.cancel_callback,
            callback_group=ReentrantCallbackGroup()
        )
        #subscription to get joints 
    def joint_state_callback(self,msg):
            self.curr_joints = msg.position


        
    #check if goal joint is valid - arr length check ws 1 currently just check if theres 6 joints
    def goal_callback(self, request):
        if len(request.joint_goal) ==6: ### 
            return GoalResponse.ACCEPT
        else:
            self.get_logger().info("Goal does not have 6 joints")
            return GoalResponse.REJECT
        

    def handle_accepted_callback(self, goal_handle):
        # only have robot doing 1 action at a time
        with self.goal_lock:
            if self.goal_handle is not None and self.goal_handle.is_active:
                self.goal_handle.abort()
            self.goal_handle = goal_handle
            goal_handle.execute()

    def cancel_callback(self):
        # cancel request
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):## page 8
        # move and look at results
        #publishing feedback
        feedback_msg = JointPTP.Feedback()
        result_msg = JointPTP.Result()
        goal_joints = goal_handle.request.joint_goal
        while True:
            feedback_msg.joint_present = self.curr_joints
            goal_handle.publish_feedback(feedback_msg)
            if math.dist(goal_joints,feedback_msg.joint_present) < 3:
                self.get_logger().info("Goal Achieved")
                return result_msg.succcess == True
            else:
                
                self.get_logger().info("Goal Failed")
                return result_msg.succcess == False

        if goal.is_cancel_requested:
            goal.cancelled()
            self.get_logger().info("Goal Cancelled")
            return #action.Result()
        
        temp = feedback_msg.sequence[i] + feedback_msg.sequence[i-1]
        feedback_msg.sequence.append(temp)
        goal.publish_feedback(feedback_msg)

        with self.goal_lock:
            if not goal.is_active:
                self.get_logger().info("Goal aborted")
                return #result
            
        
        result.sequence = feedback_msg.sequence

        self.get_logger().info("Returning result: {result.sequence}")
        
        while rclpy.ok():
            
            time.sleep(0.1) 
        
        return result_msg

def main(args=None):
    try:
        with rclpy.init(args=args):
            node = JointPTPNode()
            # Multi-threaded executor required for action servers
            executor = MultiThreadedExecutor()
            rclpy.spin(node, executor=executor)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass

if __name__ == '__main__':
    main()