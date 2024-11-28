import numpy as np

# Path to the sparse.npy file
sparse_path = "C:\\Users\\reidr\\OneDrive\\Desktop\\APP\\Financial-Planning-APP\\dlrm\\torchrec_dlrm\\transactions_npy\\sparse.npy"

# Maximum number of embeddings per feature (from --num_embeddings_per_feature)
num_embeddings = [5, 6, 26]  # Replace with your actual embedding sizes if different

# Load the sparse.npy file
sparse_data = np.load(sparse_path)

# Clamp values to ensure they are within bounds
clamped_data = np.clip(sparse_data, a_min=0, a_max=np.array(num_embeddings) - 1)

# Save the clamped sparse data to a new file
clamped_sparse_path = "C:\\Users\\reidr\\OneDrive\\Desktop\\APP\\Financial-Planning-APP\\dlrm\\torchrec_dlrm\\transactions_npy\\sparse_clamped.npy"
np.save(clamped_sparse_path, clamped_data)

print(f"Preprocessed sparse data saved to: {clamped_sparse_path}")
