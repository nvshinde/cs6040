import matplotlib.pyplot as plt
import argparse

# Function to read data from a file
def read_data_from_file(filename):
    data = []
    with open(filename, 'r') as f:
        for line in f:
            start, end = map(float, line.strip().split(', '))
            data.append((start, end))
    return data

# Main function
def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Plot packet transmission states from a data file.')
    parser.add_argument('filename', type=str, help='Path to the input data file')
    args = parser.parse_args()

    # Read data from file
    data = read_data_from_file(args.filename)

    # Prepare data for plotting
    x_values_full = []
    y_values_full = []

    last_time = 0

    # Fill in the gaps with 0
    for start, end in data:
        # Fill in the values from last_time to start with 0
        if last_time < start:
            x_values_full.append(last_time)
            y_values_full.append(0)
        # Add the start time and 1
        x_values_full.append(start)
        y_values_full.append(1)
        # Add the end time and 1
        x_values_full.append(end)
        y_values_full.append(1)
        last_time = end  # Update last_time to the end of the current packet

    # Append a final point at the last time with 0
    x_values_full.append(last_time)
    y_values_full.append(0)

    # Plotting
    plt.figure(figsize=(10, 5))
    plt.step(x_values_full, y_values_full, where='post', linestyle='-', color='b', label='Transmission State')
    plt.title("Packet Transmission States Over Time")
    plt.xlabel("Time")
    plt.ylabel("Transmission State")
    plt.yticks([0, 1], ['No Transmission', 'Transmission'])
    plt.grid(True)
    plt.legend()

    # Show the plot
    plt.show()

# Entry point for the script
if __name__ == "__main__":
    main()
