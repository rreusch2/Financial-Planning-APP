import tensorflow as tf
import tf_quant_finance as tff
import numpy as np
import matplotlib.pyplot as plt

def simulate_gbm(
    initial_value=1000.0,
    mean_return=0.07,
    volatility=0.2,
    time_horizon=10,
    steps_per_year=252,
    num_simulations=5000,
    plot=False,
):
    """
    Simulates Geometric Brownian Motion (GBM) for financial forecasting.

    Parameters:
        initial_value (float): Starting value (e.g., initial investment or stock price).
        mean_return (float): Annualized return (e.g., 0.07 for 7%).
        volatility (float): Annualized volatility (e.g., 0.2 for 20%).
        time_horizon (int): Time horizon in years.
        steps_per_year (int): Number of time steps per year.
        num_simulations (int): Number of simulation paths.
        plot (bool): Whether to generate plots.

    Returns:
        dict: A dictionary containing:
            - final_values: List of final values from all simulations.
            - expected_value: Expected value after the time horizon.
    """
    try:
        # Define the GBM process
        gbm = tff.models.GenericItoProcess(
            drift_fn=lambda t, x: mean_return * tf.ones_like(x),
            volatility_fn=lambda t, x: volatility * tf.ones_like(x),
        )

        # Define time points for simulation
        times = np.linspace(0.0, time_horizon, int(time_horizon * steps_per_year))

        # Simulate paths
        samples = gbm.sample_paths(
            initial_state=[initial_value],
            times=times,
            num_samples=num_simulations,
            seed=42,
        )

        # Analyze the final values
        final_values = samples[:, -1, 0].numpy()  # Get the last value of each path
        expected_value = tf.reduce_mean(final_values).numpy()

        if plot:
            # Plot simulation paths
            plt.figure(figsize=(10, 6))
            for i in range(100):  # Plot 100 paths for visualization
                plt.plot(times, samples[i, :, 0], alpha=0.3, linewidth=0.7)
            plt.title(f"Simulated Paths of GBM Over {time_horizon} Years")
            plt.xlabel("Time (Years)")
            plt.ylabel("Value")
            plt.grid()
            plt.show()

            # Plot histogram of final values
            plt.figure(figsize=(10, 6))
            plt.hist(final_values, bins=50, alpha=0.7, color="blue")
            plt.title(f"Distribution of Final Values After {time_horizon} Years")
            plt.xlabel("Value ($)")
            plt.ylabel("Frequency")
            plt.grid()
            plt.show()

        # Return results
        return {
            "final_values": final_values.tolist(),
            "expected_value": expected_value,
        }

    except Exception as e:
        return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    result = simulate_gbm(plot=True)
    if "error" not in result:
        print(f"Expected Value After 10 Years: ${result['expected_value']:,.2f}")
    else:
        print(f"Error: {result['error']}")
