from simulator.environment import Env
import pygame
from simulator import globals
from simulator.utils import get_lane_borders
from simulator.traffic_router import TrafficRouter
from simulator.host_vehicle import HostVehicle
import simulator
import math
import random
from simulator.traffic import SingleTargetAhead

pygame.font.init()


class Simulator:
    def __init__(self, number_of_lanes, speed_limit, initial_speed=27, show_parameter_panel=True, show_odometer_panel=True, size="medium"):
        globals.set_screen_size(size=size)
        self.screen = pygame.display.set_mode((globals.WIDTH,globals.HEIGHT))

        pygame.display.set_caption(globals.CAPTION)
        clock = pygame.time.Clock()
        self.num_lanes = number_of_lanes
        # create sprites
        self.env = Env(number_of_lanes, show_horizontal_line=False)
        self.road_borders = self.env.get_sidwalk_road_borders()
        self.lane_borders = get_lane_borders(self.road_borders[0], num_lane=self.num_lanes)
        self.show_parameter_panel = show_parameter_panel

        # ----------------------------------- SETUP TRAFFIC ---------------------------------
        # speed range of traffic objects
        low_speed = math.floor(0.7 * speed_limit)
        high_speed = math.floor(0.9 * speed_limit)

        # router class needs below parameters
        # gap_offset: offset for gap between two adjacent traffic objects (Y axis)
        # traffic_object_start_point: start point for adding new traffic objects (Y axis)
        # has_speed_change: should change the speed of traffic objects or not
        # speed_change_gap_low and speed_change_gap_high: range for spent time to change the speed of traffic objects
        self.traffic_router = TrafficRouter(self.lane_borders, self.road_borders, self.num_lanes,
                                            speed_range=[low_speed, high_speed], gap_offset=0,
                                            traffic_object_start_point=0, has_speed_change=True,
                                            new_traffic_object_probability=0.33)

        # -------------------------------- SETUP HOST VEHICLE ---------------------------------
        self.host_vehicle = HostVehicle(globals.HOST_VEHICLE_IMAGES, self.lane_borders,
                                        p_bottom_pos=(0,globals.HEIGHT),
                                        p_init_lng_spd=initial_speed, p_max_spd=speed_limit, is_motorcycle=False, lane=1)
        self.host_odometer_value = 0
        self.show_odometer_panel = show_parameter_panel
        # initialize scenario variables
        self.running = True
        self.perception = {}
        self.lanes_speed = [0] * self.num_lanes
        self.clock = pygame.time.Clock()
        self.quit_game = False

    def step(self, action="", user_given_odometer_value=0):

        if self.running:

            # update host vehicle based on user input
            self.host_vehicle.update(action)

            # update the environment
            self.env.update(speed=self.host_vehicle.get_speed())

            # manage traffic objects (we should provide host vehicle lane in each step to manage the speed of that lane by specified step)
            targets, self.lanes_speed = self.traffic_router.update(host_speed=self.host_vehicle.get_speed())

            # get the self.perception from host vehicle
            self.perception = self.host_vehicle.sensing(targets)

            # update odometer value
            self.host_odometer_value += self.host_vehicle.get_speed()

            # check the possible collision
            self.running = self.perception.running

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quit_game = True
                    self.perception.running = False
                    pygame.quit()
                    exit()

            self.render(user_given_odometer_value=user_given_odometer_value)
            return self.perception
        else:
            self.render(user_given_odometer_value=user_given_odometer_value)
            return {"running":False}

    def render(self, user_given_odometer_value=0):
        if not self.quit_game:
            if self.running:
                self.env.render(self.screen)

                # render the traffic objects
                self.traffic_router.render(self.screen)

                # render host vehicle
                self.host_vehicle.render(self.screen)

                if self.show_parameter_panel:

                    data = [
                        f"host_speed: {self.perception.host_speed}",
                        f"host_lane: {self.perception.host_lane}",
                        "",
                        f"forward dist: {self.perception.forward_target.dist}",
                        f"forward speed: {self.perception.forward_target.vy}",
                        "",
                        f"left_lane_available: {self.perception.left_lane_available}",
                        f"left dist: {self.perception.left_forward_target.dist}",
                        f"left speed: {self.perception.left_forward_target.vy}",
                        "",
                        f"right_lane_available: {self.perception.right_lane_available}",
                        f"right dist: {self.perception.right_forward_target.dist}",
                        f"right speed: {self.perception.right_forward_target.vy}",
                        "",
                        f"lanes speed: {self.lanes_speed}"
                    ]

                pygame.draw.rect(self.screen, globals.YELLOW, pygame.Rect(globals.PARAMETER_PANEL_YELLOW_RECT_START_X, globals.PARAMETER_PANEL_YELLOW_RECT_START_y, globals.PARAMETER_PANEL_YELLOW_RECT_WIDTH, globals.PARAMETER_PANEL_YELLOW_RECT_HEIGHT))
                pygame.draw.rect(self.screen, globals.BLACK, pygame.Rect(globals.PARAMETER_PANEL_BLACK_RECT_START_X, globals.PARAMETER_PANEL_BLACK_RECT_START_y, globals.PARAMETER_PANEL_BLACK_RECT_WIDTH, globals.PARAMETER_PANEL_BLACK_RECT_HEIGHT))
                for idx in range(len(data)):
                    font = pygame.font.Font('freesansbold.ttf', globals.PANEL_FONT_SIZE)
                    text = font.render(data[idx], True, globals.WHITE)
                    self.screen.blit(text, (globals.PARAMETER_PANEL_TEXT_START_X, globals.PARAMETER_PANEL_BLACK_RECT_START_y + globals.PADDING + idx * globals.PARAMETER_PANEL_TEXT_HEIGHT))

            if self.show_odometer_panel:
                pygame.draw.rect(self.screen, globals.YELLOW, pygame.Rect(globals.ODOMETER_PANEL_START_POINT, globals.ODOMETER_PANEL_START_POINT, globals.ODOMETER_PANEL_WIDTH + 2 * globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_HEIGHT + 2 * globals.ODOMETER_PANEL_BORDER_WIDTH))
                pygame.draw.rect(self.screen, globals.BLACK, pygame.Rect(globals.ODOMETER_PANEL_START_POINT + globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_START_POINT + globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_WIDTH, globals.ODOMETER_PANEL_HEIGHT))
                font = pygame.font.Font('freesansbold.ttf', globals.PANEL_FONT_SIZE)
                text = font.render("ODOMETER PANEL", True, globals.YELLOW)
                self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2))
                font = pygame.font.Font('freesansbold.ttf', globals.ODOMETER_FONT_SIZE)
                text = font.render(f"USER VALUE: {user_given_odometer_value:,}", True, globals.WHITE)
                self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2 + globals.ODOMETER_PANEL_HEIGHT * 1 / 3))
                text = font.render(f"REAL VALUE: {self.host_odometer_value:,}", True, globals.WHITE)
                self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2 + globals.ODOMETER_PANEL_HEIGHT * 2 / 3))

                pygame.display.flip()
            else:
                # draw/render
                self.env.render(self.screen)
                font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
                text = font.render('SIMULATION ENDED', True, globals.GREEN, globals.BLUE)
                text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
                self.screen.blit(text, text_rect)
                pygame.display.flip()

            pygame.display.update()
            self.clock.tick(globals.FPS)


class MultiLaneHighwayAVSimulator:
    def __init__(self, speed_limit=30, initial_speed=27, show_parameter_panel=True, size="medium"):
        globals.set_screen_size(size=size)
        self.screen = pygame.display.set_mode((globals.WIDTH,globals.HEIGHT))

        pygame.display.set_caption(globals.CAPTION)
        clock = pygame.time.Clock()
        self.num_lanes = 3
        # create sprites
        self.env = Env(self.num_lanes, show_horizontal_line=False)
        self.road_borders = self.env.get_sidwalk_road_borders()
        self.lane_borders = get_lane_borders(self.road_borders[0], num_lane=self.num_lanes)
        self.show_parameter_panel = show_parameter_panel

        # ----------------------------------- SETUP TRAFFIC ---------------------------------
        # speed range of traffic objects
        low_speed = math.floor(0.7 * speed_limit)
        high_speed = math.floor(0.9 * speed_limit)

        # router class needs below parameters
        # gap_offset: offset for gap between two adjacent traffic objects (Y axis)
        # traffic_object_start_point: start point for adding new traffic objects (Y axis)
        # has_speed_change: should change the speed of traffic objects or not
        # speed_change_gap_low and speed_change_gap_high: range for spent time to change the speed of traffic objects
        self.traffic_router = TrafficRouter(self.lane_borders, self.road_borders, self.num_lanes,
                                            speed_range=[low_speed, high_speed], gap_offset=0,
                                            traffic_object_start_point=0, has_speed_change=True,
                                            new_traffic_object_probability=0.33)

        # -------------------------------- SETUP HOST VEHICLE ---------------------------------
        self.host_vehicle = HostVehicle(globals.HOST_VEHICLE_IMAGES, self.lane_borders,
                                        p_bottom_pos=(0,globals.HEIGHT),
                                        p_init_lng_spd=initial_speed, p_max_spd=speed_limit, is_motorcycle=False, lane=1)
        self.host_odometer_value = 0
        self.show_odometer_panel = show_parameter_panel
        # initialize scenario variables
        self.running = True
        self.perception = {}
        self.lanes_speed = [0] * self.num_lanes
        self.clock = pygame.time.Clock()
        self.quit_game = False

    def step(self, action=""):
        if self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quit_game = True
                    self.perception.running = False
                    pygame.quit()
                    exit()
            # update host vehicle based on user input
            self.host_vehicle.update(action)

            # update the environment
            self.env.update(speed=self.host_vehicle.get_speed())

            # manage traffic objects (we should provide host vehicle lane in each step to manage the speed of that lane by specified step)
            targets, self.lanes_speed = self.traffic_router.update(host_speed=self.host_vehicle.get_speed())

            # get the self.perception from host vehicle
            self.perception = self.host_vehicle.sensing(targets)

            # update odometer value
            self.host_odometer_value += self.host_vehicle.get_speed()

            # check the possible collision
            self.running = self.perception.running

            self.render()
            return self.perception
        else:
            return {"running":False}

    def render(self):
        if self.running:
            self.env.render(self.screen)

            # render the traffic objects
            self.traffic_router.render(self.screen)

            # render host vehicle
            self.host_vehicle.render(self.screen)

            if self.show_parameter_panel:

                data = [
                    f"host_speed: {self.perception.host_speed}",
                    f"host_lane: {self.perception.host_lane}",
                    "",
                    f"forward dist: {self.perception.forward_target.dist}",
                    f"forward speed: {self.perception.forward_target.vy}",
                    "",
                    f"left_lane_available: {self.perception.left_lane_available}",
                    f"left dist: {self.perception.left_forward_target.dist}",
                    f"left speed: {self.perception.left_forward_target.vy}",
                    "",
                    f"right_lane_available: {self.perception.right_lane_available}",
                    f"right dist: {self.perception.right_forward_target.dist}",
                    f"right speed: {self.perception.right_forward_target.vy}",
                    "",
                    f"lanes speed: {self.lanes_speed}"
                ]

                pygame.draw.rect(self.screen, globals.YELLOW, pygame.Rect(globals.PARAMETER_PANEL_YELLOW_RECT_START_X, globals.PARAMETER_PANEL_YELLOW_RECT_START_y, globals.PARAMETER_PANEL_YELLOW_RECT_WIDTH, globals.PARAMETER_PANEL_YELLOW_RECT_HEIGHT))
                pygame.draw.rect(self.screen, globals.BLACK, pygame.Rect(globals.PARAMETER_PANEL_BLACK_RECT_START_X, globals.PARAMETER_PANEL_BLACK_RECT_START_y, globals.PARAMETER_PANEL_BLACK_RECT_WIDTH, globals.PARAMETER_PANEL_BLACK_RECT_HEIGHT))
                for idx in range(len(data)):
                    font = pygame.font.Font('freesansbold.ttf', globals.PANEL_FONT_SIZE)
                    text = font.render(data[idx], True, globals.WHITE)
                    self.screen.blit(text, (globals.PARAMETER_PANEL_TEXT_START_X, globals.PARAMETER_PANEL_BLACK_RECT_START_y + globals.PADDING + idx * globals.PARAMETER_PANEL_TEXT_HEIGHT))

            pygame.display.flip()
        else:
            # draw/render
            self.env.render(self.screen)
            font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
            text = font.render('SIMULATION ENDED', True, globals.GREEN, globals.BLUE)
            text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()

        pygame.display.update()
        self.clock.tick(globals.FPS)


class OdometerCalculationSimulator:
    def __init__(self, size="medium", initial_speed=25, odometer_threshold=500, speed_range=[5, 10], is_while_loop=False):
        self.is_while_loop = is_while_loop
        self.speed_range = speed_range
        globals.set_screen_size(size=size)
        self.screen = pygame.display.set_mode((globals.WIDTH,globals.HEIGHT))

        pygame.display.set_caption(globals.CAPTION)
        self.num_lanes = 1
        self.odometer_threshold = odometer_threshold
        # create sprites
        self.env = Env(self.num_lanes, show_horizontal_line=False)

        self.road_borders = self.env.get_sidwalk_road_borders()
        self.lane_borders = get_lane_borders(self.road_borders[0], num_lane=self.num_lanes)

        # -------------------------------- SETUP HOST VEHICLE ---------------------------------
        self.host_vehicle = HostVehicle(globals.HOST_VEHICLE_IMAGES, self.lane_borders,
                                        p_bottom_pos=(0,globals.HEIGHT),
                                        p_init_lng_spd=initial_speed, is_motorcycle=False, lane=0)
        self.host_odometer_value = 0
        self.user_given_odometer_value = 0
        # initialize scenario variables
        self.running = True
        self.clock = pygame.time.Clock()
        self.quit_game = False

        self.time_step = 1
        self.message = ""

    def step(self, action="", user_given_odometer_value=0):
        self.user_given_odometer_value = user_given_odometer_value

        if self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quit_game = True
                    pygame.quit()
                    exit()

            if (self.host_odometer_value - self.odometer_threshold) >= self.host_vehicle.get_speed():
                self.message = "FAIL: TRAVELLED PAST THE REQUIRED DISTANCE!"
            elif (self.host_odometer_value - self.odometer_threshold) < 0 and action == "stop":
                self.message = "FAIL: DID NOT TRAVEL THE REQUIRED DISTANCE!"
            elif action == "stop":
                self.message = "PASS: TRAVELLED THE CORRECT DISTANCE!"

            self.render()
            if self.is_while_loop:
                new_speed = random.randint(self.speed_range[0], self.speed_range[1])
                self.host_vehicle.set_speed(new_speed)

            # update host vehicle based on user input
            if globals.DEBUG:
                print(f"speed outside env: {self.host_vehicle.get_speed()}")
            self.host_vehicle.update("")

            # update the environment
            self.env.update(speed=self.host_vehicle.get_speed())

            # update odometer value
            self.host_odometer_value += self.host_vehicle.get_speed()

            return self.host_vehicle.get_speed(), self.time_step

        else:
            self.render()
            return {"running":False}

    def render(self):
        if not self.quit_game:
            if self.running:
                self.env.render(self.screen)

                # render host vehicle
                self.host_vehicle.render(self.screen)

            pygame.draw.rect(self.screen, globals.YELLOW, pygame.Rect(globals.ODOMETER_PANEL_START_POINT, globals.ODOMETER_PANEL_START_POINT, globals.ODOMETER_PANEL_WIDTH + 2 * globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_HEIGHT + 2 * globals.ODOMETER_PANEL_BORDER_WIDTH))
            pygame.draw.rect(self.screen, globals.BLACK, pygame.Rect(globals.ODOMETER_PANEL_START_POINT + globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_START_POINT + globals.ODOMETER_PANEL_BORDER_WIDTH, globals.ODOMETER_PANEL_WIDTH, globals.ODOMETER_PANEL_HEIGHT))
            font = pygame.font.Font('freesansbold.ttf', globals.PANEL_FONT_SIZE)
            text = font.render("ODOMETER PANEL", True, globals.YELLOW)
            self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2))
            font = pygame.font.Font('freesansbold.ttf', globals.ODOMETER_FONT_SIZE)
            color = globals.RED
            if int(self.user_given_odometer_value) == int(self.host_odometer_value):
                color = globals.GREEN

            text = font.render(f"USER VALUE: {self.user_given_odometer_value:,}", True, globals.WHITE)
            self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2 + globals.ODOMETER_PANEL_HEIGHT * 1 / 4))
            delta = self.host_odometer_value - self.user_given_odometer_value
            text = font.render(f"ERROR: {delta:,}", True, color)
            self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2 + globals.ODOMETER_PANEL_HEIGHT * 2 / 4))
            text = font.render(f"SPEED: {self.host_vehicle.get_speed()}", True, globals.WHITE)
            self.screen.blit(text, (globals.ODOMETER_PANEL_START_POINT * 2, globals.ODOMETER_PANEL_START_POINT * 2 + globals.ODOMETER_PANEL_HEIGHT * 3 / 4))

            if self.message != "":
                font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
                if "PASS" in self.message:
                    text = font.render(self.message, True, globals.GREEN, globals.BLACK)
                else:
                    text = font.render(self.message, True, globals.RED, globals.BLACK)
                text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
                self.screen.blit(text, text_rect)

            pygame.display.flip()
        else:
            # draw/render
            self.env.render(self.screen)
            font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
            text = font.render('SIMULATION ENDED', True, globals.GREEN, globals.BLUE)
            text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
            self.screen.blit(text, text_rect)
            pygame.display.flip()

            pygame.display.update()
            self.clock.tick(globals.FPS)


class ParallelParkingSimulator:
    def __init__(self, initial_speed=20, size="medium"):
        globals.set_screen_size(size=size)
        self.screen = pygame.display.set_mode((globals.WIDTH,globals.HEIGHT))

        pygame.display.set_caption(globals.CAPTION)
        self.num_lanes = 2
        # create sprites
        self.env = Env(self.num_lanes, show_horizontal_line=True)
        self.clock = pygame.time.Clock()

        self.check_position_list = []
        self.step_position_list = []
        self.step_image_list = []
        self.x_image = pygame.transform.scale(pygame.image.load(globals.X_IMAGE).convert_alpha(), globals.CHECK_SIZE)
        self.check_image = pygame.transform.scale(pygame.image.load(globals.CHECK_IMAGE).convert_alpha(), globals.CHECK_SIZE)
        for i in range(0, 7):
            self.step_image_list.append(pygame.transform.scale(pygame.image.load(globals.STEPS_IMAGES[i]).convert_alpha(), globals.STEP_SIZE))
            self.check_position_list.append(globals.PARKING_PANEL_START_POINT * 2 + i * globals.STEP_GAP)
            self.step_position_list.append(globals.PARKING_PANEL_START_POINT * 2 + i * globals.STEP_GAP)

        self.itr_step = 0
        self.required_action = "forward"
        self.failure_message = ""
        self.done_steps = [False, False, False, False, False, False, False]
        self.done_steps = [False, False, False, False, False, False, False]

        self.road_borders = self.env.get_sidwalk_road_borders()
        self.lane_borders = get_lane_borders(self.road_borders[0], num_lane=self.num_lanes)
        self.get_horizontal_line_location = self.env.get_horizontal_line_location()
        # add two globals.VEHICLES
        self.targets = pygame.sprite.Group()
        image_idx = random.randint(0,3)
        target_1 = SingleTargetAhead(globals.VEHICLE_IMAGES[image_idx], self.lane_borders,
                                     p_bottom_pos=(0,self.get_horizontal_line_location[1][1] - 30),
                                     p_init_lng_spd=0, is_motorcycle=False, lane=1)
        image_idx = random.randint(0,3)
        target_2 = SingleTargetAhead(globals.VEHICLE_IMAGES[image_idx], self.lane_borders,
                                     p_bottom_pos=(0,self.get_horizontal_line_location[2][1] + 30),
                                     p_init_lng_spd=0, is_motorcycle=False, lane=1, set_top=True)
        self.targets.add(target_1)
        self.targets.add(target_2)

        # -------------------------------- SETUP HOST VEHICLE ---------------------------------
        self.host_vehicle = HostVehicle(globals.HOST_VEHICLE_IMAGES, self.lane_borders,
                                        p_bottom_pos=(0,globals.HEIGHT),
                                        p_init_lng_spd=initial_speed, is_motorcycle=False, lane=0)

        # initialize scenario variables
        self.running = True
        self.clock = pygame.time.Clock()
        self.quit_game = False

    def step(self, action):
        if self.running and self.failure_message == "":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.quit_game = True
                    pygame.quit()
                    exit()

            if action == self.required_action and self.failure_message == "":
                # update host vehicle based on user input
                self.host_vehicle.update(action)

                # update the environment
                self.env.update(speed=0)

                if self.itr_step == globals.PARALLEL_PARKING_STEPS[0]:
                    self.done_steps[0] = True
                    self.required_action = "turn_right"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[1]:
                    self.done_steps[1] = True
                    self.required_action = "reverse"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[2]:
                    self.done_steps[2] = True
                    self.required_action = "turn_left"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[3]:
                    self.done_steps[3] = True
                    self.required_action = "reverse"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[4]:
                    self.done_steps[4] = True
                    self.required_action = "turn_left"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[5]:
                    self.done_steps[5] = True
                    self.required_action = "reverse"
                elif self.itr_step == globals.PARALLEL_PARKING_STEPS[6]:
                    self.done_steps[6] = True
                    self.required_action = "show_result"

                self.itr_step += 1
            elif self.required_action != "done":

                self.failure_message = f"You should use '{self.required_action}' action here"

            if globals.DEBUG:
                print(f"step: {self.itr_step} - action: {action} - next required_action: {self.required_action}")

            self.render()

        else:
            self.render()
            return {"running":False}

    def render(self):
        if not self.quit_game:
            if self.failure_message == "":
                self.env.render(self.screen, show_sidewalk_objects=False)

                self.targets.draw(self.screen)

                # render host vehicle
                self.host_vehicle.parrallel_parking_render(self.screen)

            if self.required_action == "show_result":
                font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
                text = font.render("WELL DONE!", True, globals.GREEN, globals.BLUE)
                text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
                self.screen.blit(text, text_rect)
        else:
            self.env.render(self.screen)

            self.targets.draw(self.screen)

            # render host vehicle
            self.host_vehicle.parrallel_parking_render(self.screen)

            font = pygame.font.Font('freesansbold.ttf', globals.FONT_SIZE)
            text = font.render(self.failure_message, True, globals.GREEN, globals.BLUE)
            text_rect = text.get_rect(center=(globals.WIDTH / 2, globals.HEIGHT / 2))
            self.screen.blit(text, text_rect)

        for i in range(0, 7):
            self.screen.blit(self.step_image_list[i], (globals.PARKING_PANEL_START_POINT, self.step_position_list[i]))

        for i in range(7):
            if self.done_steps[i] == True:
                self.screen.blit(self.check_image, (globals.STEP_SIZE[0] - globals.CHECK_SIZE[0], self.check_position_list[i]))
            elif self.failure_message != "":
                self.screen.blit(self.x_image, (globals.STEP_SIZE[0] - globals.CHECK_SIZE[0], self.check_position_list[i]))
                break

        pygame.display.update()
        self.clock.tick(globals.FPS)
