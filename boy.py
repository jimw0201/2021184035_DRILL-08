from pico2d import load_image, get_time

from state_machine import StateMachine, time_out, space_down, right_down, left_up, left_down, right_up, start_event, auto_run


# 상태를 클래스를 통해서 정의함.
class Idle:
    @staticmethod
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.dir = 0 # 정지 상태이다.
        boy.frame = 0
        # 현재 시간을 저장
        boy.start_time = get_time()

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3:
            boy.state_machine.add_event(('TIME_OUT',0))

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class Sleep:
    @staticmethod
    def enter(boy, e):
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1: #
            boy.image.clip_composite_draw(boy.frame * 100, 300, 100, 100,
                                          3.141592 / 2,  # 90도 회전
                                          '',  # 좌우상하 반전 X
                                          boy.x - 25, boy.y - 25, 100, 100)
        elif boy.face_dir == -1:
            boy.image.clip_composite_draw(boy.frame * 100, 200, 100, 100,
                                          -3.141592 / 2,  # 90도 회전
                                          '',  # 좌우상하 반전 X
                                          boy.x + 25, boy.y - 25, 100, 100)

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir = 1 # 오른쪽 방향
            boy.action = 1
        elif left_down(e) or right_up(e):
            boy.dir = -1
            boy.action = 0
        boy.frame = 0

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.x += boy.dir * boy.speed
        boy.frame = (boy.frame + 1) % 8
        if boy.x < 25:
            boy.x = 25
            boy.dir = 0
        elif boy.x > 775:
            boy.x = 775
            boy.dir = 0

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)

class AutoRun:
    @staticmethod
    def enter(boy, e):
        if boy.face_dir == 1:
            boy.dir = 1
        else:
            boy.dir = -1
        boy.action = 1
        boy.frame = 0
        boy.speed = 20
        boy.scale = 2
        boy.auto_run_time = get_time()

    @staticmethod
    def exit(boy, e):
        if boy.face_dir == 1:
            boy.action = 3
        else:
            boy.action = 2
        boy.speed = 5
        boy.scale = 1

    @staticmethod
    def do(boy):
        boy.x += boy.dir * boy.speed
        boy.frame = (boy.frame + 1) % 8
        if boy.x < 50 or boy.x > 750:
            boy.dir *= -1
            boy.face_dir *= -1
        if get_time() - boy.auto_run_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))

    @staticmethod
    def draw(boy):
        width, height = 100, 100
        scaled_w = width * boy.scale
        scaled_h = height * boy.scale
        if boy.face_dir == 1:
            boy.image.clip_draw(boy.frame * width, boy.action * height, width, height, boy.x, boy.y + 40, scaled_w, scaled_h)
        else:
            boy.image.clip_composite_draw(boy.frame * width, boy.action * height, width, height, 0, 'h', boy.x, boy.y + 40, scaled_w, scaled_h)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.speed = 5
        self.scale = 1
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) # 소년 객체의 state machine 생성
        self.state_machine.start(Idle) # 초기 상태가 Idle
        self.state_machine.set_transitions(
            {
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle},
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Sleep, auto_run: AutoRun},
                Sleep: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, space_down: Idle},
                AutoRun: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()
        # self.frame = (self.frame + 1) % 8

    def handle_event(self, event):
        # event : 입력 이벤트 key mouse
        # 우리가 state machine 전달해줄껀 (  ,  )
        self.state_machine.add_event(
            ('INPUT',event)
        )

    def draw(self):
        self.state_machine.draw()
        # self.image.clip_draw(self.frame * 100, self.action * 100, 100, 100, self.x, self.y)