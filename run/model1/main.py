import torch
from torch.nn import Module, Linear, CrossEntropyLoss
from torch.optim import Adam

device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
assert str(device)=='cuda', f"Torch device is not 'cuda' but '{device}'"

class MLP(Module):
  def __init__(self):
    super(MLP, self).__init__()
    self.linear = Linear(28*28, 10)
  def forward(self, x):
    out = self.linear(x)
    return out

model = MLP().to(device)
optimizer = Adam(model.parameters())
criterion = CrossEntropyLoss()




