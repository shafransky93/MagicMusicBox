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
octave = 3  # Initial octave
waveform_var = None
selected_note = None

# Parameters
duration_ms = 100
sample_rate = 48000

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
    global oscillator_on, cutoff_frequency, cutoff_enabled

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

        if cutoff_enabled:
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
        root.after(1, update_tone)  # Update every millisecond


# Create the main window
root = tk.Tk()
root.title("Synth")

# Global cutoff frequency state variable
cutoff_enabled = False

# Function to toggle the cutoff frequency filter on and off
def toggle_cutoff_frequency():
    global cutoff_enabled
    cutoff_enabled = not cutoff_enabled


# Create a frame for the oscillator controls
oscillator_frame = tk.Frame(root)
oscillator_frame.pack(pady=10)

# Amplitude slider
amplitude_label = tk.Label(oscillator_frame, text="Amplitude")
amplitude_label.pack(side="left")
amplitude_slider = tk.Scale(oscillator_frame, from_=0, to=1, resolution=0.01, orient="horizontal")
amplitude_slider.set(0.5)
amplitude_slider.pack(side="left", padx=0)

# Frequency slider
frequency_label = tk.Label(oscillator_frame, text="Frequency (Hz)")
frequency_label.pack(side="left")
frequency_slider = tk.Scale(oscillator_frame, from_=20, to=2000, resolution=1, orient="horizontal")
frequency_slider.set(440)
frequency_slider.pack(side="left", padx=0)

# Pulse width (Duty Cycle) slider
pulse_width_label = tk.Label(oscillator_frame, text="Pulse Width")
pulse_width_label.pack(side="left")
pulse_width_slider = tk.Scale(oscillator_frame, from_=0, to=100, orient="horizontal")
pulse_width_slider.set(50)  # Set initial pulse width to 50%
pulse_width_slider.pack(side="left", padx=0)

# Attack, Decay, Sustain, and Release sliders
adsr_frame = tk.Frame(root)
adsr_frame.pack(pady=0)

attack_label = tk.Label(adsr_frame, text="Attack (ms)")
attack_label.pack(side="left")
attack_slider = tk.Scale(adsr_frame, from_=0, to=1000, resolution=1, orient="horizontal")
attack_slider.set(10)
attack_slider.pack(side="left", padx=0)

decay_label = tk.Label(adsr_frame, text="Decay (ms)")
decay_label.pack(side="left")
decay_slider = tk.Scale(adsr_frame, from_=0, to=1000, resolution=1, orient="horizontal")
decay_slider.set(50)
decay_slider.pack(side="left", padx=0)

sustain_label = tk.Label(adsr_frame, text="Sustain (%)")
sustain_label.pack(side="left")
sustain_slider = tk.Scale(adsr_frame, from_=0, to=100, orient="horizontal")
sustain_slider.set(70)
sustain_slider.pack(side="left", padx=0)

release_label = tk.Label(adsr_frame, text="Release (ms)")
release_label.pack(side="left")
release_slider = tk.Scale(adsr_frame, from_=0, to=1000, resolution=1, orient="horizontal")
release_slider.set(100)
release_slider.pack(side="left", padx=0)

# Waveform selection
waveform_frame = tk.Frame(root)
waveform_frame.pack(pady=10)

waveform_label = tk.Label(waveform_frame, text="Waveform:")
waveform_label.pack(side="left", padx=5)

waveform_var = tk.StringVar(value="Sine")

sine_radio = tk.Radiobutton(waveform_frame, text="Sine", variable=waveform_var, value="Sine")
triangle_radio = tk.Radiobutton(waveform_frame, text="Triangle", variable=waveform_var, value="Triangle")
sawtooth_radio = tk.Radiobutton(waveform_frame, text="Sawtooth", variable=waveform_var, value="Sawtooth")
square_radio = tk.Radiobutton(waveform_frame, text="Square", variable=waveform_var, value="Square")

sine_radio.pack(side="left", padx=10)
triangle_radio.pack(side="left", padx=10)
sawtooth_radio.pack(side="left", padx=10)
square_radio.pack(side="left", padx=10)

# Create a frame for the cutoff frequency controls
cutoff_frame = tk.Frame(root)
cutoff_frame.pack(pady=0)

# Create a button to toggle cutoff frequency filter
cutoff_button = tk.Button(cutoff_frame, text="Toggle Cutoff Frequency", command=toggle_cutoff_frequency)
cutoff_button.pack(side="left", padx=0)

# Cutoff frequency slider
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)

cutoff_frequency_label = tk.Label(filter_frame, text="Cutoff Frequency (Hz)")
cutoff_frequency_label.pack(side="left")
cutoff_frequency_slider = tk.Scale(filter_frame, from_=1, to=20000, resolution=1, orient="horizontal")
cutoff_frequency_slider.set(10000)  # Set an initial cutoff frequency
cutoff_frequency_slider.pack(side="left", padx=10)

# Initialize the filter with an initial cutoff frequency
cutoff_frequency = cutoff_frequency_slider.get()
nyquist_frequency = 0.5 * sample_rate
b, a = signal.butter(1, cutoff_frequency / nyquist_frequency, btype='low', analog=False)

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
octave_frame = tk.Frame(root)
octave_frame.pack(pady=10)

octave_up_button = tk.Button(octave_frame, text="Octave Up", command=lambda: change_octave('up'))
octave_down_button = tk.Button(octave_frame, text="Octave Down", command=lambda: change_octave('down'))

octave_up_button.pack(side="left")
octave_down_button.pack(side="left")

# Notes buttons
notes_label = tk.Label(root, text="Notes")
notes_label.pack()
notes_buttons_frame = tk.Frame(root)
notes_buttons_frame.pack()

for note in notes:
    note_button = tk.Button(notes_buttons_frame, text=note, command=lambda note=note: change_notes(note),pady=10,padx=30)
    note_button.pack(side="left")

# Generate button
generate_button = tk.Button(root, text="Toggle Oscillator", command=toggle_oscillator)
generate_button.pack(pady=10)


# Create a frame for the oscilloscope
oscilloscope_frame = tk.Frame(root)
oscilloscope_frame.pack(pady=10)

# Create a Figure for the oscilloscope
fig = plt.figure(figsize=(6, 3))
canvas = FigureCanvasTkAgg(fig, master=oscilloscope_frame)
canvas.get_tk_widget().pack()


# Function to toggle the visibility of the oscilloscope
def toggle_oscilloscope():
    if oscilloscope_frame.winfo_ismapped():
        oscilloscope_frame.pack_forget()
    else:
        oscilloscope_frame.pack(pady=10)

# Create a button for hiding/showing the oscilloscope
oscilloscope_button = tk.Button(root, text="Hide/Show Oscilloscope", command=toggle_oscilloscope)
oscilloscope_button.pack()


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
root.bind('t', lambda event: toggle_cutoff_frequency())

# Bind key press events
root.bind('<KeyPress>', handle_key)
root.bind('<Up>', simulate_octave_up)
root.bind('<Down>', simulate_octave_down)

# Function to create the Help tab
def create_help_tab():
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    
    help_text = """
    - Use the 'Amplitude' slider to adjust the volume of the sound.
    - Use the 'Frequency' slider to select the desired frequency in Hertz (Hz).
    - Use the 'Pulse Width' slider to control the pulse width for square waveforms.
    - Use the 'Attack', 'Decay', 'Sustain', and 'Release' sliders to shape the envelope.
    - Choose a waveform type (Sine, Triangle, Sawtooth, Square) using the radio buttons.
    - Toggle the 'Cutoff Frequency' filter using the button.
    - Octave Up and Octave Down buttons change the selected octave.
    - Notes buttons (C, D, E, F, G, A, B) select a note.
    - Press the corresponding letter keys (a, s, d, f, g, h, j) for notes.
    - Press 'Space' to toggle the oscillator on and off.
    - Press 'q' for Sine waveform, 'w' for Triangle, 'e' for Sawtooth, 'r' for Square.
    - Press 't' to toggle the Cutoff Frequency filter on and off.
    
    Enjoy making music with the Synth App!
    """
    
    help_label = tk.Label(help_window, text=help_text, justify="left")
    help_label.pack(padx=20, pady=20)

# Function to create the About tab
def create_about_tab():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    
    about_text = """
    Synth App v1.0
    Created by Benjamin Shafransky
    
    This application allows you to generate and play various audio waveforms using various controls.

    Inspired by teh song ’81: How to Play the Synthesizer by The Magnetic Fields
    
    Have fun experimenting with different sounds!

    If interested in my other projects visit my github!

    https://github.com/shafransky93
    """
    
    about_label = tk.Label(about_window, text=about_text, justify="left", padx=20, pady=20)
    about_label.pack()
    

# Function to create the About tab
def create_how_tab():
    how_window = tk.Toplevel(root)
    how_window.title("How to play")
    
    how_text = """
    The Magnetic Fields - '81 How to Play the Synthesizer:

    Take a single oscillator
    Producing a drone
    Send it to the wave shaper
    Altering the tone
    This can be a triangle
    Sawtooth or a square
    Modulate the pulse width
    Nobody will care

    This is how to play the synthesizer
    This is how to play the synthesizer

    Now go to the filter bank
    Low, high, band or notch
    Fiddle with the cutoff point
    Pour yourself a Scotch
    Modern filters oscillate
    All by themselves
    It sounds like you're torturing
    Little metal elves

    This is how to play the synthesizer
    This is how to play the synthesizer

    Nextly, shape the envelope
    AKA ADSR
    Attack, delay, sustain, release
    Which means how loud you are
    One millisecond to the next
    Whether you pluck or lurch
    Or ooze like an organist
    In a Venusian church

    This is how to play the synthesizer
    This is how to play the synthesizer

    Now you play the synthesizer
    Don't be lazy now
    Make it hiss like rattlesnakes
    Or moo like a cow
    Crash like a hundred marbles
    Smashing on the floor
    You can make a thousand sounds
    Never heard before

    This is how to play the synthesizer
    This is how to play the synthesizer

    """
    
    how_label = tk.Label(how_window, text=how_text, justify="left", padx=20, pady=20)
    how_label.pack()
    

def exit_application():
    root.destroy()
    
# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=exit_application)

# Create a Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="Help", command=create_help_tab)
help_menu.add_command(label="About", command=create_about_tab)
help_menu.add_command(label="How", command=create_how_tab)

# Start the GUI main loop
root.mainloop()
