import numpy as np

class NeuralNetwork:
    def __init__(self, layer_sizes, activation_functions):
        self.layer_sizes = layer_sizes
        self.activation_functions = activation_functions
        self.num_layers = len(layer_sizes)
        self.weights = [np.random.randn(layer_sizes[i], layer_sizes[i+1]) for i in range(self.num_layers - 1)]
        self.biases = [np.zeros((1, layer_sizes[i+1])) for i in range(self.num_layers - 1)]

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def relu(self, x):
        return np.maximum(0, x)

    def relu_derivative(self, x):
        return np.where(x > 0, 1, 0)

    def forward(self, inputs):
        activations = [inputs]
        weighted_inputs = []

        for i in range(self.num_layers - 1):
            weighted_input = np.dot(activations[-1], self.weights[i]) + self.biases[i]
            weighted_inputs.append(weighted_input)

            if self.activation_functions[i] == 'sigmoid':
                activation = self.sigmoid(weighted_input)
            elif self.activation_functions[i] == 'relu':
                activation = self.relu(weighted_input)

            activations.append(activation)

        return activations, weighted_inputs

    def backward(self, inputs, targets, learning_rate):
        activations, weighted_inputs = self.forward(inputs)
        num_samples = inputs.shape[0]

        # Calculate the loss
        loss = targets - activations[-1]

        # Backpropagation
        deltas = [loss]
        for i in range(self.num_layers - 2, -1, -1):
            if self.activation_functions[i] == 'sigmoid':
                delta = deltas[-1] * self.sigmoid_derivative(activations[i+1])
            elif self.activation_functions[i] == 'relu':
                delta = deltas[-1] * self.relu_derivative(activations[i+1])

            deltas.append(delta)

        deltas.reverse()

        # Update weights and biases
        for i in range(self.num_layers - 1):
            self.weights[i] += learning_rate * np.dot(activations[i].T, deltas[i]) / num_samples
            self.biases[i] += learning_rate * np.sum(deltas[i], axis=0, keepdims=True) / num_samples

    def train(self, inputs, targets, learning_rate, epochs):
        for epoch in range(epochs):
            self.backward(inputs, targets, learning_rate)

            if epoch % 100 == 0:
                activations, _ = self.forward(inputs)
                loss = np.mean(np.square(targets - activations[-1]))
                print(f"Epoch {epoch}, Loss: {loss}")

if __name__ == "__main__":
    layer_sizes = [2, 4, 4, 1]
    activation_functions = ['relu', 'relu', 'sigmoid']
    nn = NeuralNetwork(layer_sizes, activation_functions)

    # Generate some random training data
    inputs = np.array([[0, 0], [0, 1], [1, 0], [1, 1]])
    targets = np.array([[0], [1], [1], [0]])

    # Train the neural network
    nn.train(inputs, targets, learning_rate=0.1, epochs=10000)

    # Test the trained neural network
    test_input = np.array([[0, 0]])
    test_output = nn.forward(test_input)
    print(f"Test Output: {test_output[0][-1]}")
