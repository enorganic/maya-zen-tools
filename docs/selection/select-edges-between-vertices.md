# Select Edges Between Vertices

## Default Options

With the default options, "Select Edges Between Vertices" will select the
edge path with the fewest number of possible edges between two or more
vertices.

<p><video src="../../assets/videos/select-edges-between-vertices.mp4" controls=true /></p>

## Use Selection Order

If your selected vertices form a path with multiple directional changes,
you'll want to check the "Use Selection Order" option for the most predictable
results:

<p><video src="../../assets/videos/select-edges-between-vertices-selection-order.mp4" controls=true /></p>

## Close the Loop

If you want your selection to form a closed loop, you *must* have selected
"Use Selection Order", *and* "Close":

<p><video src="../../assets/videos/select-edges-between-vertices-selection-order-closed.mp4" controls=true /></p>


## Why?

Why is this tool useful when there is already a "shortest edge path" tool
in Maya?

-   ZenTools "Select Edges Between Vertices" uses a different (better)
    algorithm. The path selected always has the *fewest number* of edges.
    This means that edge loops are followed more predictably.
-   ZenTools "Select Edges Between Vertices" does not clear prior *edge*
    selections on your mesh on execution. This allows easy selection of
    multiple non-contiguous (such as parallel) edge paths, which is highly
    desirable when selecting edges for use with
    [Loft Distribute Vertices Between Edges](
    ../modeling/loft-distribute-vertices-between-edges.md)
