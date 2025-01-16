# Curve Distribute Between UVs

## Default Options

With the default options, "Curve Distribute Between UVs" will distribute
UVs forming path between your selected UVs along a (dynamically created and
not retained) NURBS curve passing between the UVs you've selected:

<p><video src="../../assets/videos/curve-distribute-between-uvs.mp4" controls=true /></p>

Note: The UVs selected adhere to the same logic as
[Select UVs Between UVs](selection/select-uvs-between-uvs.md).

## Proportional Distribution

The default distribution type for this tool is "Uniform", however you can
select "Proportional" distribution in order to distribute UVs with spacing
relative to their distribution in 3d space:

<p><video src="../../assets/videos/curve-distribute-between-uvs-proportional.mp4" controls=true /></p>

## Use Selection Order

If your selected UVs form a path with multiple directional changes,
you'll want to check the "Use Selection Order" option for the most predictable
results:

<p><video src="../../assets/videos/curve-distribute-between-uvs-selection-order.mp4" controls=true /></p>

## Close the Loop

If you want the curve along which your UVs are distributed to form a
closed loop, you *must* have selected "Use Selection Order", *and* "Close":

<p><video src="../../assets/videos/curve-distribute-between-uvs-selection-order-closed.mp4" controls=true /></p>
