#!/usr/bin/env python
import rospy
from sensor_msgs.msg import Joy
import termios
import tty
import sys
import select

class KeyboardJoyPublisher:
    def __init__(self):
        rospy.init_node('keyboard_joy_publisher')
        self.pub = rospy.Publisher('joy', Joy, queue_size=10)
        self.rate = rospy.Rate(10)  # 10Hz

        # 버튼 맵핑: 키 => 인덱스
        self.key_to_button = {
            'w': 0,
            'a': 1,
            's': 2,
            'd': 3,
            ' ': 4,
        }
        self.num_buttons = 5
        self.axes = [0.0] * 2  # 예: 왼/오른쪽 조이스틱 가상 입력
        rospy.loginfo("Keyboard to Joy mapper started. Keys: w/a/s/d/space")

    def get_key(self):
        # 터미널 설정을 바꿔 키보드 입력을 즉시 읽어옴
        tty.setraw(sys.stdin.fileno())
        select.select([sys.stdin], [], [], 0)
        key = sys.stdin.read(1)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def run(self):
        self.settings = termios.tcgetattr(sys.stdin)
        try:
            while not rospy.is_shutdown():
                key = self.get_key()
                buttons = [0] * self.num_buttons

                if key in self.key_to_button:
                    buttons[self.key_to_button[key]] = 1
                    rospy.loginfo(f"Key '{key}' pressed -> Button {self.key_to_button[key]}")

                # Joy 메시지 구성
                joy_msg = Joy()
                joy_msg.header.stamp = rospy.Time.now()
                joy_msg.axes = self.axes
                joy_msg.buttons = buttons

                self.pub.publish(joy_msg)
                self.rate.sleep()
        except rospy.ROSInterruptException:
            pass
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)

if __name__ == '__main__':
    node = KeyboardJoyPublisher()
    node.run()
