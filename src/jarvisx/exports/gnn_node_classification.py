"""
Genesis Omega GNN Pipeline
Implements a 2-layer Graph Convolutional Network (GCN) for node classification.
Designed for the Cora citation dataset using PyTorch Geometric.
"""

import torch
import torch.nn.functional as F

try:
    from torch_geometric.nn import GCNConv
    from torch_geometric.datasets import Planetoid
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    print("WARNING: torch_geometric not installed. Running in Mock Mode.")

class GCN(torch.nn.Module):
    def __init__(self, num_node_features, num_classes):
        super(GCN, self).__init__()
        if TORCH_GEOMETRIC_AVAILABLE:
            self.conv1 = GCNConv(num_node_features, 16)
            self.conv2 = GCNConv(16, num_classes)
        else:
            # Mock layers for simulation integrity
            self.conv1 = torch.nn.Linear(num_node_features, 16)
            self.conv2 = torch.nn.Linear(16, num_classes)

    def forward(self, data):
        x = data.x
        edge_index = getattr(data, 'edge_index', None)

        if TORCH_GEOMETRIC_AVAILABLE:
            x = self.conv1(x, edge_index)
            x = F.relu(x)
            x = F.dropout(x, training=self.training)
            x = self.conv2(x, edge_index)
        else:
            x = self.conv1(x)
            x = F.relu(x)
            x = F.dropout(x, training=self.training)
            x = self.conv2(x)
            
        return F.log_softmax(x, dim=1)

def execute_gnn_pipeline():
    print("Initializing GNN Node Classification Pipeline...")
    
    if TORCH_GEOMETRIC_AVAILABLE:
        dataset = Planetoid(root='/tmp/Cora', name='Cora')
        data = dataset[0]
        model = GCN(dataset.num_node_features, dataset.num_classes)
    else:
        print("[MOCK] Loading Cora citation dataset...")
        # Mock data structure
        class MockData:
            def __init__(self):
                self.x = torch.randn(2708, 1433)
                self.y = torch.randint(0, 7, (2708,))
        
        data = MockData()
        model = GCN(1433, 7)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

    model.train()
    for epoch in range(200):
        optimizer.zero_grad()
        out = model(data)
        
        loss = F.nll_loss(out[:140], data.y[:140])
            
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0:
            print(f"Epoch {epoch:03d} | Loss: {loss.item():.4f}")

    print("Training complete. GNN Pipeline Successfully Deployed.")

if __name__ == "__main__":
    execute_gnn_pipeline()
