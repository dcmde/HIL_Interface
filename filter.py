import numpy as np
import random
import matplotlib.pyplot as plt
from scipy import signal

# Define the parameters
frequency = 400  # Frequency of the sinusoidal wave in Hz

sampling_rate = 50000  # Sampling rate in Hz
duration = 0.01  # Duration of the signal in seconds

# Calculate the total number of samples
num_samples = int(duration * sampling_rate)

# Generate time array
t = np.arange(num_samples) / sampling_rate

# Generate the sinusoidal wave
wave = np.sin(2 * np.pi * frequency * t)

# Generate random values
random_values = np.array([random.random() for _ in range(num_samples)])*0.2

# Generate the random sequence over the sinusoidal wave
random_sequence = wave + random_values

cutoff_freq = 4000  # Cutoff frequency in Hz
tau = 2*3.1416/cutoff_freq

a0 = np.exp(-1/sampling_rate/tau)

print(a0)
print(1-a0)

# Define the filter coefficients
order = 4  # Filter order
normalized_cutoff_freq = cutoff_freq / (0.5 * sampling_rate)  # Normalize cutoff frequency
b, a = signal.butter(order, normalized_cutoff_freq, btype='low', analog=False)

filtered_signal_1 = signal.lfilter(np.array([1-a0]), np.array([1, -a0]), random_sequence)
filtered_signal_2 = signal.lfilter(b, a, random_sequence)

# Plot the random sequence over the sinusoidal wave
plt.plot(random_sequence)
plt.plot(filtered_signal_1)
plt.plot(filtered_signal_2)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Random Sequence over Sinusoidal Wave')
plt.show()