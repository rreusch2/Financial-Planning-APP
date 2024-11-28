# Portfolio Parameters
portfolio_weights = [0.6, 0.4]  # 60% stock, 40% bond
asset_returns = [0.08, 0.03]  # Expected annual returns for stocks and bonds
asset_volatility = [0.2, 0.1]  # Volatility for stocks and bonds
correlation_matrix = [[1.0, 0.3], [0.3, 1.0]]  # Correlation between assets

# Convert to covariance matrix
covariance_matrix = np.outer(asset_volatility, asset_volatility) * correlation_matrix

# Simulate portfolio returns
portfolio_paths = []
for _ in range(num_simulations):
    daily_returns = np.random.multivariate_normal(
        mean=asset_returns,
        cov=covariance_matrix,
        size=(time_horizon * steps_per_year)
    )
    cumulative_returns = np.cumprod(1 + daily_returns, axis=0)
    weighted_returns = cumulative_returns @ portfolio_weights
    portfolio_paths.append(weighted_returns[-1])  # Final portfolio value

# Analyze portfolio
mean_portfolio_value = np.mean(portfolio_paths)
print(f"Expected Portfolio Value After {time_horizon} Years: ${mean_portfolio_value:,.2f}")
