#!/usr/bin/env python

import tkinter as tk
import numpy as np
import simpleaudio as sa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Variables to keep track of the oscillator state and play_obj
oscillator_on = False
play_obj = None  # Store the play_obj for reuse
audio_samples = None  # Store the audio samples for reuse

# Global slider variables
amplitude_slider = None
frequency_slider = None
pulse_width_slider = None
waveform_var = None

# Function to generate and play the drone sound
def toggle_oscillator():
    global oscillator_on, play_obj, audio_samples

    # If the oscillator is currently on, stop it
    if oscillator_on:
        play_obj.stop()
        oscillator_on = False
        plt.clf()  # Clear the oscilloscope plot
    else:
        # Get the amplitude, frequency, waveform type, and pulse width from the sliders
        amplitude = amplitude_slider.get()
        frequency = frequency_slider.get()
        waveform_type = waveform_var.get()
        pulse_width = pulse_width_slider.get() / 100.0  # Convert pulse width to a fraction

        # Calculate the time array
        t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), endpoint=False)

        # Create the selected waveform (including pulse width for square wave)
        if waveform_type == "Sine":
            wave_func = lambda t: amplitude * np.sin(2 * np.pi * frequency * t)
        elif waveform_type == "Triangle":
            wave_func = lambda t: amplitude * (2 * np.abs(2 * frequency * t - 1) - 1)
        elif waveform_type == "Sawtooth":
            wave_func = lambda t: amplitude * (2 * (frequency * t - np.floor(0.5 + frequency * t)))
        elif waveform_type == "Square":
            wave_func = lambda t: amplitude * (np.floor(2 * frequency * t + pulse_width) % 2)

        # Generate the waveform
        audio_samples = (wave_func(t) * 32767).astype(np.int16)

        # Play the audio using simpleaudio
        play_obj = sa.play_buffer(audio_samples, 1, 2, sample_rate)
        oscillator_on = True

        # Update the tone continuously while the oscillator is on
        update_tone()

def update_tone():
    global oscillator_on
    if oscillator_on:
        # Get the updated amplitude, frequency, waveform type, and pulse width from the sliders
        amplitude = amplitude_slider.get()
        frequency = frequency_slider.get()
        waveform_type = waveform_var.get()
        pulse_width = pulse_width_slider.get() / 100.0  # Convert pulse width to a fraction

        # Calculate the time array
        t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), endpoint=False)

        # Create the selected waveform (including pulse width for square wave)
        if waveform_type == "Sine":
            wave_func = lambda t: amplitude * np.sin(2 * np.pi * frequency * t)
        elif waveform_type == "Triangle":
            wave_func = lambda t: amplitude * (2 * np.abs(2 * frequency * t - 1) - 1)
        elif waveform_type == "Sawtooth":
            wave_func = lambda t: amplitude * (2 * (frequency * t - np.floor(0.5 + frequency * t)))
        elif waveform_type == "Square":
            wave_func = lambda t: amplitude * (np.floor(2 * frequency * t + pulse_width) % 2)

        # Generate the waveform
        audio_samples = (wave_func(t) * 32767).astype(np.int16)

        # Update the audio being played
        play_obj = sa.play_buffer(audio_samples, 1, 2, sample_rate)

        # Plot the waveform on the oscilloscope
        plt.clf()
        plt.plot(t, audio_samples)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("Oscilloscope")
        plt.xlim(0, 0.01)
        canvas.draw()

        # Schedule the next update
        root.after(300, update_tone)  # Update every 300 milliseconds

# Parameters
duration_ms = 5000
sample_rate = 44100

# Create the main window
root = tk.Tk()
root.title("Drone Sound Generator")

# Amplitude slider
amplitude_label = tk.Label(root, text="Amplitude")
amplitude_label.pack()
amplitude_slider = tk.Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal")
amplitude_slider.set(0.5)
amplitude_slider.pack()

# Frequency slider
frequency_label = tk.Label(root, text="Frequency (Hz)")
frequency_label.pack()
frequency_slider = tk.Scale(root, from_=20, to=2000, resolution=1, orient="horizontal")
frequency_slider.set(220)
frequency_slider.pack()

# Pulse width (Duty Cycle) slider
pulse_width_label = tk.Label(root, text="Pulse Width")
pulse_width_label.pack()
pulse_width_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
pulse_width_slider.set(50)  # Set initial pulse width to 50%
pulse_width_slider.pack()

# Waveform selection
waveform_label = tk.Label(root, text="Waveform")
waveform_label.pack()

waveform_var = tk.StringVar(value="Sine")

sine_radio = tk.Radiobutton(root, text="Sine", variable=waveform_var, value="Sine")
triangle_radio = tk.Radiobutton(root, text="Triangle", variable=waveform_var, value="Triangle")
sawtooth_radio = tk.Radiobutton(root, text="Sawtooth", variable=waveform_var, value="Sawtooth")
square_radio = tk.Radiobutton(root, text="Square", variable=waveform_var, value="Square")

sine_radio.pack()
triangle_radio.pack()
sawtooth_radio.pack()
square_radio.pack()

# Create a Figure for the oscilloscope
fig = plt.figure(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Generate button
generate_button = tk.Button(root, text="Toggle Oscillator", command=toggle_oscillator)
generate_button.pack()

# Start the GUI main loop
root.mainloop()
