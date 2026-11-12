# One small C++ step: encode evidence without changing Alex

```cpp
const auto evidence = alex.boundary_evidence(
    {10, 10, 1000}, "retina-and-body:window-1");
```

`alex` is our existing `PersonModel`. The result owns its observation and its
provenance string. There are no borrowed pointers to preserve.

```cpp
evidence.visually_active.value(); // 10 / (10 + 5) = 2/3
evidence.bodily_active.value();   // also 2/3
```

Both predicates can hold strongly. Their sum may exceed one because these are
fuzzy memberships of different predicates. Neither expression says there is a
two-thirds probability that the source is external.

```cpp
evidence.bayesian_external_probability;
```

That is a different quantity: the posterior supplied by Alex's configured
observation model. HRL and GRRLE can take evidence-derived unary strengths and
combine them with compatibility rules. Their resulting strengths keep their
own meaning. A compatibility rule is an assumption we can test and replace.

`boundary_evidence()` is `const`: encoding does not alter Alex's Body or Will.
The existing `perceive()` and attended-integration behavior stay available.

Question for our next small step: why can the two memberships sum to more than
one while a two-hypothesis probability distribution must sum to one?
