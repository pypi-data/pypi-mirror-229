from .vehicle import Vehicle


class HostVehicle(Vehicle):
    def __init__(self, p_image, lane_borders, lane=0, p_bottom_pos=(0,0), p_init_lat_spd=0, p_init_lng_spd=0, p_max_spd=30, p_cycle_limit=1000, is_motorcycle=False):
        super().__init__(p_image, lane_borders, p_bottom_pos, p_init_lat_spd, p_init_lng_spd, p_max_spd, is_motorcycle)

        # set target speed
        self.set_speed(self.vy)

        # set target lane
        self.go_to_lane(lane)

        # simulation attributes
        self.status = 1  # (1; active, -1: terminate)
        self.cycle = 0
        self.cycle_limit = p_cycle_limit

    def update(self, action):
        if action == "speed_up":
            self.speed_up()
        elif action == "speed_down":
            self.speed_down()
        elif action == "shift_left":
            self.move_left()
        elif action == "shift_right":
            self.move_right()
        elif action == "stop":
            self.stop()
        elif action == "turn_right":
            self.turn_right()
        elif action == "turn_left":
            self.turn_left()
        elif action == "forward":
            self.forward()
        elif action == "reverse":
            self.reverse()
        else:
            pass

    # renders the host vehicle on the display
    def render(self, screen):
        screen.blit(self.image, self.get_rect_position())
