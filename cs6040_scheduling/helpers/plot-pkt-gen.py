import matplotlib.pyplot as plt
import argparse

# Main function
def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Plot points where value is 1 from a data file.')
    parser.add_argument('filename', type=str, help='Path to the input data file')
    args = parser.parse_args()

    # Initialize lists to hold the data
    times = []
    vals = []

    # Read the data from the text file
    with open(args.filename, 'r') as file:
        next(file)  # Skip the header line
        for line in file:
            time, val = line.strip().split(',')
            times.append(float(time))
            vals.append(int(val))

    # Filter the data where val is 1
    filtered_times = [t for t, v in zip(times, vals) if v == 1]
    filtered_vals = [v for v in vals if v == 1]

    # Plot the data
    plt.figure(figsize=(10, 5))
    plt.scatter(filtered_times, filtered_vals, color='blue', label='Value = 1', s=50)

    # Customize the plot
    plt.title('Points where Value is 1')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.yticks([0, 1], ['0', '1'])  # Only show 0 and 1 on the y-axis
    plt.grid()
    plt.axhline(y=1, color='gray', linestyle='--', lw=0.5)  # Optional: horizontal line at y=1
    plt.legend()
    plt.tight_layout()

    # Show the plot
    plt.show()

# Entry point for the script
if __name__ == "__main__":
    main()
