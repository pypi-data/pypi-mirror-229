import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.model_selection import train_test_split
from torch import nn

from sampo.scheduler.selection.metrics import one_hot_encode


class NeuralNet(nn.Module):
    def __init__(self, input_size: int, layer_size: int, layer_count: int, out_size: int, learning_rate=0.001):
        super(NeuralNet, self).__init__()
        self._layers_count = layer_count
        self._linear0 = torch.nn.Linear(input_size, layer_size)
        for i in range(layer_count - 2):
            self.__dict__[f'_linear{i + 1}'] = torch.nn.Linear(layer_size, layer_size)
        self.__dict__[f'_linear{layer_count - 1}'] = torch.nn.Linear(layer_size, out_size)
        self._learning_rate = learning_rate
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def forward(self, x):
        x = self._linear0(x)
        for i in range(1, self._layers_count):
            linear = self.__dict__[f'_linear{i}']
            x = F.relu(x)
            x = linear(x)
        x = F.softmax(x, dim=0)
        return x

    def fit(self, x, y, epochs=10):
        criterion = torch.nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.parameters(), lr=self._learning_rate)

        # Train the model
        total_step = len(x)
        for epoch in range(epochs):
            for i, (image, label) in enumerate(zip(x, y)):
                # Move tensors to the configured device
                image = image.to(self._device)
                label = label.to(self._device)

                # Forward pass
                outputs = self(image)
                loss = criterion(outputs, label.float())

                # Backpropagation and optimization
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                if (i + 1) % 100 == 0:
                    print('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'
                          .format(epoch + 1, epochs, i + 1, total_step, loss.item()))

    def predict(self, x: list) -> torch.tensor:
        result = []
        with torch.no_grad():
            for image in x:
                image = image.to(self._device)
                outputs = self(image)
                _, predicted = torch.max(outputs.data, 0)
                result.append(torch.tensor(one_hot_encode(predicted, 3)))
        return result


def load_dataset(filename: str) -> tuple[list, list, list, list]:
    df = pd.read_csv(filename)
    df.reset_index()
    x_train, x_test, y_train, y_test = train_test_split(df.drop('label', axis=1).to_numpy(), df['label'].to_numpy(),
                                                        stratify=df['label'].to_numpy())
    return [torch.Tensor(v) for v in x_train[:, 1:]],\
           [torch.Tensor(v) for v in x_test[:, 1:]], \
           [torch.Tensor(one_hot_encode(v, 3)) for v in y_train], \
           [torch.Tensor(one_hot_encode(v, 3)) for v in y_test]
