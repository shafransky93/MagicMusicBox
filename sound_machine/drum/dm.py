#!/usr/bin/env python

import pygame
import random

# Initialize Pygame
pygame.init()

# Define the key-sound mapping
key_sound_mapping = {
    pygame.K_a: pygame.mixer.Sound('sound_a.wav'),
    pygame.K_s: pygame.mixer.Sound('sound_s.wav'),
    pygame.K_d: pygame.mixer.Sound('sound_d.wav'),
    # Add more key-sound pairs as needed
}

# Set up the display
initial_resolution = (800, 800)
screen = pygame.display.set_mode(initial_resolution)
pygame.display.set_caption('Sound Player')

# Initialize a dictionary to store key press times
key_press_times = {}

# Initialize sound channels for concurrent playback
num_channels = 8  # You can adjust this value as needed
pygame.mixer.set_num_channels(num_channels)
sound_channels = [pygame.mixer.Channel(i) for i in range(num_channels)]

# Variables for controlling the flashing circle
flash_circle_radius = 50
flash_last_update = pygame.time.get_ticks()
flash_active = False
circle_expand_duration = 500  # Time to expand the circle (0.5 seconds)

# Fullscreen mode flag and resolutions
fullscreen = False
fullscreen_resolution = (1920, 1080)  # Adjust this to your desired fullscreen resolution

# Function to toggle fullscreen mode
def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode(fullscreen_resolution, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(initial_resolution)

# Function to generate a random neon color with dominance
def random_neon_color():
    dominance = random.choice(["r", "g", "b"])  # Choose a dominant color component

    if dominance == "r":
        r = random.randint(220, 255)  # Red component dominant
        g = random.randint(0, 200)    # Green component subdued
        b = random.randint(0, 200)    # Blue component subdued
    elif dominance == "g":
        r = random.randint(0, 200)    # Red component subdued
        g = random.randint(220, 255)  # Green component dominant
        b = random.randint(0, 200)    # Blue component subdued
    else:  # "b" dominance
        r = random.randint(0, 200)    # Red component subdued
        g = random.randint(0, 200)    # Green component subdued
        b = random.randint(220, 255)  # Blue component dominant

    return (r, g, b)

# Function to draw the expanding and fading circle
def draw_flash_circle():
    global flash_active, circle_expanding, circle_fading, circle_start_time, circle_size, circle_opacity

    if flash_active:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - circle_start_time

        if circle_expanding:
            if elapsed_time >= circle_expand_duration:
                circle_expanding = False
                circle_start_time = current_time
            else:
                circle_size = 2.5*flash_circle_radius * (elapsed_time / circle_expand_duration)

        pygame.draw.circle(screen, flash_color, flash_circle_location, int(circle_size), 0)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check if a key is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                toggle_fullscreen()
            elif event.key in key_sound_mapping:
                sound = key_sound_mapping[event.key]
                channel = sound_channels.pop(0)  # Get an available channel
                channel.play(sound)
                key_press_times[event.key] = pygame.time.get_ticks()
                sound_channels.append(channel)  # Return the used channel to the end

                # Generate random location for flashing circle within the screen dimensions
                flash_circle_location = (random.randint(0, screen.get_width()), random.randint(0, screen.get_height()))

                # Generate a random neon color
                flash_color = random_neon_color()

                flash_active = True
                circle_expanding = True
                circle_fading = False
                circle_start_time = pygame.time.get_ticks()
                circle_size = 0
                circle_opacity = 255

    # Draw the flashing circle
    draw_flash_circle()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
