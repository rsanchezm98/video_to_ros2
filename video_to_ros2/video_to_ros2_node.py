import cv2
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VideoPublisher(Node):
    def __init__(self):
        super().__init__('video_publisher_node')

        self.declare_parameter('frame_rate', 15.0)
        self.declare_parameter('video_file', '/media/rsm/Extreme SSD/rodrigo_vision/video_demo/auto.webm')
        self.declare_parameter('base_frame', 'camera')
        self.declare_parameter('output_topic', 'raw_image')
        self.declare_parameter('resize_percent', 60)

        self.frame_rate = self.get_parameter('frame_rate').value
        self.video_file = self.get_parameter('video_file').value
        self.base_frame = self.get_parameter('base_frame').value
        self.output_topic = self.get_parameter('output_topic').value
        self.resize_percent = self.get_parameter('resize_percent').value

        self.video_capture = cv2.VideoCapture(self.video_file)
        if not self.video_capture.isOpened():
            self.get_logger().info("Error opening video. Check it out")
            return

        self.create_timer(1./self.frame_rate, self.timer_callback)
        self.pub = self.create_publisher(Image, self.output_topic, 1)

        self.video_completed = False
        self.cv_bridge = CvBridge()
        
        

    def timer_callback(self):
        if not self.video_completed:
            if self.video_capture.isOpened():
                ret, frame = self.video_capture.read()
                if ret:
                    #init_ts = self.get_clock().now()
                    width = int(frame.shape[1] * self.resize_percent / 100)
                    height = int(frame.shape[0] * self.resize_percent / 100)
                    dim = (width, height)
                    frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)                    
                    img = self.cv_bridge.cv2_to_imgmsg(frame)
                    img.header.frame_id = self.base_frame
                    img.header.stamp = self.get_clock().now().to_msg()
                    self.pub.publish(img) # this will spend more time when higher image size [up to it does not accomplish the frame rate]
                    #elapsed = self.get_clock().now() - init_ts
                    #self.get_logger().info("Elapsed callback time: %f ms" % (elapsed.nanoseconds/1.0e6))
                else:
                    self.video_capture.release()
                    self.get_logger().info("Video completed...")
                    self.video_completed = True
            

def Main(args = None):
    rclpy.init(args=args)
    video_pub_class = VideoPublisher()
    video_pub_class.get_logger().info('Node created...')
    rclpy.spin(video_pub_class)
    video_pub_class.destroy_node()
    rclpy.shutdown()    


if __name__ == '__main__':
    Main()
