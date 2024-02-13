import mouse
import pygame

BUTTON_STR = "button"
HAT_STR = "hat"
CONTROL_ENABLE_SEQUENCE = (pygame.BUTTON_X1,
                           pygame.BUTTON_X2)
CONTROL_ENABLE_SEQUENCE_KEYS_COUNT = len(CONTROL_ENABLE_SEQUENCE)


def control_mouse_with_joystick():
    pygame.init()
    pygame.joystick.init()
    print(pygame.joystick.get_count())

    joysticks = [pygame.joystick.Joystick(
        x) for x in range(pygame.joystick.get_count())]

    done = False
    pressed = False
    control_enabled = False
    move_direction = [0, 0]
    enable_seq_counter = 0

    print("Press BACK and START buttons 3 times to enable control")

    while not done:
        for event in pygame.event.get():  # Get the current event
            if control_enabled:
                if HAT_STR in event.dict.keys():  # Handle mouse movement
                    values = event.dict["value"]

                    if values != pygame.HAT_CENTERED:  # If the HAT is released stop the movement
                        move_direction = [values[0], values[1] * -1]
                        mouse_move(move_direction)
                        pressed = True
                    else:
                        pressed = False

                if BUTTON_STR in event.dict.keys() and event.type == pygame.JOYBUTTONDOWN:
                    # Left mouse button click
                    if event.dict[BUTTON_STR] == pygame.CONTROLLER_BUTTON_A:
                        mouse.click()
                    # Right mouse button click
                    elif event.dict[BUTTON_STR] == pygame.CONTROLLER_BUTTON_B:
                        mouse.click(mouse.RIGHT)
                    # Exit the app on Y press
                    elif event.dict[BUTTON_STR] == pygame.CONTROLLER_BUTTON_Y:
                        done = True

            # By default the app is disabled to prevent unwanted behaviour
            if BUTTON_STR in event.dict.keys() and event.type == pygame.JOYBUTTONDOWN and \
                    event.dict[BUTTON_STR] == CONTROL_ENABLE_SEQUENCE[enable_seq_counter % CONTROL_ENABLE_SEQUENCE_KEYS_COUNT]:
                enable_seq_counter += 1
            elif not BUTTON_STR in event.dict.keys() and event.type != pygame.JOYBUTTONDOWN:
                enable_seq_counter = 0

            if enable_seq_counter >= CONTROL_ENABLE_SEQUENCE_KEYS_COUNT * 3:  # Enable/Disable the app
                control_enabled = not control_enabled
                enable_seq_counter = 0

                if control_enabled:
                    print("Control enabled")
                else:
                    print("Control disabled")

        if pressed:  # Keep moving if the HAT is held
            mouse_move(move_direction)

        if pygame.joystick.get_count() == 0:  # Exit the app the joysticks disconnect
            print("Controllers disconnected. Exiting.")
            break

    pygame.joystick.quit()
    pygame.quit()


def mouse_move(move_direction):
    mouse.move(move_direction[0], move_direction[1], False, 0.001)


if __name__ == "__main__":
    control_mouse_with_joystick()
