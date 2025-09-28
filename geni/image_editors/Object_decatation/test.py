import torch
import torchvision
print("this is version of torch",torch.__version__)  # PyTorch version
print(torchvision.__version__)  # Torchvision version
print(torch.cuda.is_available())  # Check if CUDA is available
