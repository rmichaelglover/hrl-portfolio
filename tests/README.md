# ✅ `tests/` — what the engine is proven to do

```
$ pytest -q
.............                                                    [100%]
13 passed 🟢
```

Every test asserts a *behavior*, not just "it runs":

| File | 🧪 proves |
|---|---|
| `test_core.py` | correspondence recovery · noise label quarantines an outlier · a prior breaks a tie · uniform prior is well-formed |
| `test_tracking.py` | identity stays stable through motion + shuffling · ghosts → noise, dropouts survive |
| `test_consensus.py` | anchored truth propagation · sign-symmetry needs an anchor · contradiction rewards opposite truth · NLI plumbing (mocked) · claim extraction |
| `test_chess_maxims.py` | daring games refute dogma → `ish`, while sound rules stay `vtrue` |

The NLI tests use a **mock pipeline**, so CI never downloads a model. 🪶

The chess-maxims test pins exactly this verdict pattern — the dogmas your games
refute land in the gray `ish` band, the rules they don't stay `vtrue`:

![chess](../assets/chess_maxims.png)

➡️ Full gallery: [`../assets/`](../assets/README.md)
