# A small C++ training loop

```cpp
RelaxationMachine model(2, 2, 6);
Adam optimizer(model.parameters().size());
```

The model owns its parameters. The optimizer owns its running estimates of
first and second gradient moments. Constructing or destroying either is ordinary
value-based C++; no manual cleanup is necessary.

```cpp
const auto result = model.loss_gradient(example);
```

This performs a forward pass and returns a scalar loss plus one derivative for
every parameter. It has not yet changed the model.

```cpp
optimizer.update(model, result.gradient, .02);
```

This changes the parameters. The same example can now be interpreted under the
revised unary evidence and compatibility rules.

There are two different iterations:

- A **relaxation step** updates strengths for the current fixed parameters.
- A **training step** updates parameters using reference-label errors.

`forward()` is a const method. Training is the operation that changes the model.
Neither operation constitutes physical time passing in Alex's Body.

The implementation's backward pass includes the initial softmax and every
repeated injection of unary evidence. The numerical checks are what let us
trust that we have differentiated the intended machine.
