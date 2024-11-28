import os
import numpy as np

# Determine the correct file path based on the operating system
if os.name == "nt":  # For Windows
    file_path = r"C:\Users\reidr\OneDrive\Desktop\APP\Financial-Planning-APP\transactions_npy\train_labels.npy"
else:  # For Linux/WSL
    file_path = "/mnt/c/Users/reidr/OneDrive/Desktop/APP/Financial-Planning-APP/transactions_npy/train_labels.npy"

# Load the labels file
labels = np.load(file_path)

# Reshape to (n, 1)
labels = labels.reshape(-1, 1)

# Save back to the file
np.save(file_path, labels)

print(f"Labels reshaped to {labels.shape} and saved.")
