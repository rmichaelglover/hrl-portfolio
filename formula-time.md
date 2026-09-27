# Formula Time · Wings Out ✨

The formulas gathered from our chess, relaxation-labeling, and silver-marble conversations. Raw LaTeX is preserved between dollar signs so it can travel to a renderer later.

## Chess as a value labyrinth ♟️🌀

Every legal position is a state $s$. Its possible moves are $M(s)$. Under perfect play, the value is the best result available after the opponent responds:

$$
V(s)=\max_{m\in M(s)}\bigl(-V(m(s))\bigr)
$$

Terminal values can be $+1$ for a win, $0$ for a draw, and $-1$ for a loss. In practice, the labyrinth is too large to visit completely, so search remembers positions and concentrates on promising corridors.

## Relaxation labeling 🌈🏷️

Let $x_i$ be the current weight of candidate continuation $i$. Let $C_{ij}$ measure how well candidates $i$ and $j$ support one another. A projected update is:

$$
x_i^{(t+1)}=\Pi_{\Delta}\left[x_i^{(t)}+\eta\sum_j C_{ij}x_j^{(t)}\right]
$$

$\eta$ controls the step size. $\Pi_{\Delta}$ projects the labels back onto a valid simplex: non-negative weights that sum to one. Compatible lines brighten; conflicting lines fade; an explicit noise label keeps uncertainty visible.

## The GRRLE support picture 🔁

For a node $i$, a simple support functional can combine same-scale and cross-scale influence:

$$
S_i(x)=\sum_j C_{ij}x_j+\lambda_{\uparrow}P_i(x)+\lambda_{\downarrow}D_i(x)
$$

Here $P_i$ is parent support, $D_i$ is child support, and the two lambdas set the cross-scale emphasis. The object can be read as a label; the label can be promoted into a larger object.

## Monte Carlo’s silver marble ⚪🎲

Monte Carlo Tree Search balances trying unfamiliar corridors with returning to corridors that already look promising:

$$
U(s,a)=\frac{W(s,a)}{N(s,a)}+c\sqrt{\frac{\ln N(s)}{N(s,a)}}
$$

$W/N$ is the observed average outcome. The square-root term rewards exploration. Randomness scouts; memory and feedback decide where the next scouts go.

## Recursive influence 🌌

If a layer’s influence is bounded by $M\alpha^d$ with $0\leq\alpha<1$, its remaining tail after depth $D$ is bounded by:

$$
\sum_{d=D+1}^{\infty}M\alpha^d
=\frac{M\alpha^{D+1}}{1-\alpha}
$$

That is a mathematical convergence condition, not evidence that physical reality has infinite recursive depth. The distinction belongs inside the poem, too.

## Constructor lens 🛠️

$$
\mathcal{T}=\{\text{input}\to\text{output}\}
$$

An observed game demonstrates repeatable transformations: position to move, move to reply, sacrifice to attack, pawn to promotion. An unseen transformation stays a possibility to investigate, not a certainty to announce.

## The loop we like 🔄

$$
\text{sample}\to\text{observe}\to\text{remember}\to\text{update}\to\text{search again}
$$

The marble rolls. The maze learns. The human decides what the journey means. 🧠⚪🌀
