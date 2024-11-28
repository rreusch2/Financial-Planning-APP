import argparse
import numpy as np
import os
from pathlib import Path

def create_test_data(output_dir):
    """Create sample data for testing the DLRM model."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create sample data
    np.save(os.path.join(output_dir, "dense.npy"), np.random.rand(1000, 13))
    np.save(os.path.join(output_dir, "sparse.npy"), np.random.randint(0, 100, (1000, 3)))
    np.save(os.path.join(output_dir, "labels.npy"), np.random.randint(0, 2, (1000, 1)))

if __name__ == "__main__":
    # Set correct paths
    current_dir = Path(__file__).parent
    dlrm_dir = current_dir / "dlrm" / "torchrec_dlrm"
    data_dir = current_dir / "test_data"
    dlrm_main = dlrm_dir / "dlrm_main.py"

    # Validate paths
    if not dlrm_main.exists():
        raise FileNotFoundError(f"Could not find dlrm_main.py at {dlrm_main}")

    # Create test data
    create_test_data(data_dir)
    
    # Run command with correct path
    cmd = f"""python "{dlrm_main}" \
        --in_memory_binary_criteo_path "{data_dir}" \
        --epochs 2 \
        --batch_size 32 \
        --learning_rate 0.01 \
        --dense_arch_layer_sizes 64,32 \
        --over_arch_layer_sizes 32,16 \
        --embedding_dim 16 \
        --dataset_name criteo_kaggle \
        --adagrad \
        --shuffle_training_set \
        --num_embeddings_per_feature 1000,1000,1000"""
    
    # Execute command
    result = os.system(cmd)
    if result != 0:
        print(f"Error: Command failed with exit code {result}")