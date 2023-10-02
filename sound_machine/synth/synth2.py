#!/usr/bin/env python

import tkinter as tk
import numpy as np
import simpleaudio as sa
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import scipy.signal as signal

# Variables to keep track of the oscillator state and play_obj
oscillator_on = False
play_obj = None  # Store the play_obj for reuse
audio_samples = None  # Store the audio samples for reuse

# Global slider variables
amplitude_slider = None
frequency_slider = None
pulse_width_slider = None
waveform_var = None
cutoff_frequency_slider = None  # Added cutoff frequency slider

# Global octave, waveform, and selected note variables
octave = -4  # Initial octave
waveform_var = None
selected_note = None

# Parameters
duration_ms = 100
sample_rate = 44100

# Global notes dictionary
notes = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

# Function to get the frequency of the selected note
def get_note_frequency():
    global selected_note, octave
    if selected_note:
        return notes[selected_note] * (2 ** (octave - 4))
    else:
        return 0  # Return 0 if no note is selected

# Initialize audio_samples with silence
audio_samples = np.zeros(int(sample_rate * duration_ms / 1000), dtype=np.int16)

# Function to generate and play the drone sound
def toggle_oscillator():
    global oscillator_on, play_obj, audio_samples, cutoff_frequency

    # If the oscillator is currently on, stop it
    if oscillator_on:
        play_obj.stop()
        oscillator_on = False
        plt.clf()  # Clear the oscilloscope plot
    else:
        # Get the amplitude, frequency, waveform type, and pulse width from the sliders
        amplitude = amplitude_slider.get()
        frequency = get_note_frequency()
        waveform_type = waveform_var.get()
        pulse_width = pulse_width_slider.get() / 100.0  # Convert pulse width to a fraction

        # Calculate the time array
        t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), endpoint=False)

        # Inside the toggle_oscillator function
        attack_time = attack_slider.get() / 1000.0  # Convert to seconds
        decay_time = decay_slider.get() / 1000.0  # Convert to seconds
        sustain_level = sustain_slider.get() / 100.0  # Convert to a fraction
        release_time = release_slider.get() / 1000.0  # Convert to seconds

        # Calculate the total duration of the ADSR envelope
        total_duration = attack_time + decay_time + release_time

        # Create the ADSR envelope
        envelope = np.zeros_like(t)
        envelope[:int(attack_time * sample_rate)] = np.linspace(0, 1, int(attack_time * sample_rate))
        envelope[int(attack_time * sample_rate):int((attack_time + decay_time) * sample_rate)] = np.linspace(1, sustain_level, int(decay_time * sample_rate))
        envelope[int((attack_time + decay_time) * sample_rate):int((duration_ms / 1000) * sample_rate - release_time * sample_rate)] = sustain_level
        envelope[int((duration_ms / 1000) * sample_rate - release_time * sample_rate):] = np.linspace(sustain_level, 0, int(release_time * sample_rate))

        # Apply the envelope to the audio samples and convert envelope to int16
        audio_samples = (audio_samples * envelope).astype(np.int16)


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

        # Apply the filter
        audio_samples = signal.lfilter(b, a, audio_samples)

        # Play the audio using simpleaudio
        play_obj = sa.play_buffer(audio_samples, 1, 2, sample_rate)
        oscillator_on = True

        # Update the tone continuously while the oscillator is on
        update_tone()

# Function to update the tone and oscilloscope plot
def update_tone():
    global oscillator_on, cutoff_frequency

    if oscillator_on:
        # Get the updated amplitude, frequency, waveform type, and pulse width from the sliders
        amplitude = amplitude_slider.get()
        frequency = get_note_frequency()
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

        # Generate the updated waveform
        audio_samples = (wave_func(t) * 32767).astype(np.int16)

        # Calculate the updated filter coefficients
        cutoff_frequency = cutoff_frequency_slider.get()
        nyquist_frequency = 0.5 * sample_rate
        b, a = signal.butter(1, cutoff_frequency / nyquist_frequency, btype='low', analog=False)

        # Apply the filter
        audio_samples = signal.lfilter(b, a, audio_samples)

        # Update the audio being played
        play_obj = sa.play_buffer(audio_samples, 1, 2, sample_rate)

        # Plot the waveform on the oscilloscope
        plt.clf()
        plt.plot(t, audio_samples)
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("Oscilloscope")
        canvas.draw()

        # Schedule the next update
        root.after(10, update_tone)  # Update every 300 milliseconds


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
frequency_slider.set(440)
frequency_slider.pack()

# Pulse width (Duty Cycle) slider
pulse_width_label = tk.Label(root, text="Pulse Width")
pulse_width_label.pack()
pulse_width_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
pulse_width_slider.set(50)  # Set initial pulse width to 50%
pulse_width_slider.pack()

# Attack, Decay, Sustain, and Release sliders
attack_label = tk.Label(root, text="Attack (ms)")
attack_label.pack()
attack_slider = tk.Scale(root, from_=0, to=500, resolution=1, orient="horizontal")
attack_slider.set(10)
attack_slider.pack()

decay_label = tk.Label(root, text="Decay (ms)")
decay_label.pack()
decay_slider = tk.Scale(root, from_=0, to=500, resolution=1, orient="horizontal")
decay_slider.set(50)
decay_slider.pack()

sustain_label = tk.Label(root, text="Sustain (%)")
sustain_label.pack()
sustain_slider = tk.Scale(root, from_=0, to=100, orient="horizontal")
sustain_slider.set(70)
sustain_slider.pack()

release_label = tk.Label(root, text="Release (ms)")
release_label.pack()
release_slider = tk.Scale(root, from_=0, to=500, resolution=1, orient="horizontal")
release_slider.set(100)
release_slider.pack()

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

# Cutoff frequency slider
cutoff_frequency_label = tk.Label(root, text="Cutoff Frequency (Hz)")
cutoff_frequency_label.pack()
cutoff_frequency_slider = tk.Scale(root, from_=1, to=20000, resolution=1, orient="horizontal")
cutoff_frequency_slider.set(10000)  # Set an initial cutoff frequency
cutoff_frequency_slider.pack()

# Initialize the filter with an initial cutoff frequency
cutoff_frequency = cutoff_frequency_slider.get()
nyquist_frequency = 0.5 * sample_rate
b, a = signal.butter(1, cutoff_frequency / nyquist_frequency, btype='low', analog=False)

# Create a Figure for the oscilloscope
fig = plt.figure(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Function to handle octave change
def change_octave(direction):
    global octave
    if direction == 'up':
        octave += 1
    elif direction == 'down':
        octave -= 1
    frequency_slider.set(get_note_frequency())

# Function to handle notes change
def change_notes(note):
    global selected_note
    selected_note = note
    frequency_slider.set(get_note_frequency())

# Function to handle key presses
def handle_key(event):
    note_mapping = {
        'a': 'C',
        's': 'D',
        'd': 'E',
        'f': 'F',
        'g': 'G',
        'h': 'A',
        'j': 'B'
    }
    if event.char in note_mapping:
        change_notes(note_mapping[event.char])
    elif event.keysym == 'space':
        toggle_oscillator()

def simulate_octave_up(event):
    octave_up_button.invoke()

def simulate_octave_down(event):
    octave_down_button.invoke()
    
# Octave buttons
octave_up_button = tk.Button(root, text="Octave Up", command=lambda: change_octave('up'))
octave_down_button = tk.Button(root, text="Octave Down", command=lambda: change_octave('down'))
octave_up_button.pack()
octave_down_button.pack()

# Notes buttons
notes_label = tk.Label(root, text="Notes")
notes_label.pack()
notes_buttons_frame = tk.Frame(root)
notes_buttons_frame.pack()

for note in notes:
    note_button = tk.Button(notes_buttons_frame, text=note, command=lambda note=note: change_notes(note))
    note_button.pack(side="left")

# Generate button
generate_button = tk.Button(root, text="Toggle Oscillator", command=toggle_oscillator)
generate_button.pack()

# Bind keys to notes
root.bind('a', lambda event: change_notes('C'))
root.bind('s', lambda event: change_notes('D'))
root.bind('d', lambda event: change_notes('E'))
root.bind('f', lambda event: change_notes('F'))
root.bind('g', lambda event: change_notes('G'))
root.bind('h', lambda event: change_notes('A'))
root.bind('j', lambda event: change_notes('B'))

# Bind keys to waveforms
root.bind('q', lambda event: waveform_var.set("Sine"))
root.bind('w', lambda event: waveform_var.set("Triangle"))
root.bind('e', lambda event: waveform_var.set("Sawtooth"))
root.bind('r', lambda event: waveform_var.set("Square"))

# Bind key press events
root.bind('<KeyPress>', handle_key)
root.bind('<Up>', simulate_octave_up)
root.bind('<Down>', simulate_octave_down)



# Start the GUI main loop
root.mainloop()
