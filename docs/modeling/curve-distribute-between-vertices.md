# Curve Distribute Between Vertices

## Default Options

With the default options, "Curve Distribute Between Vertices" will distribute
vertices forming an edge path between your selected vertices along a
(dynamically created and not retained) NURBS curve passing between the vertices
you've selected:

<p><video src="../../assets/videos/curve-distribute-between-vertices.mp4" controls=true /></p>

Note: The vertices selected adhere to the same logic as
[Select Edges Between Vertices](../selection/select-edges-between-vertices.md).

## Proportional Distribution

The default distribution type for this tool is "Uniform", however you can
select "Proportional" distribution in order to retain the same relative spacing
between the redistributed vertices:

<p><video src="../../assets/videos/curve-distribute-between-vertices-proportional.mp4" controls=true /></p>

## Use Selection Order

If your selected vertices form a path with multiple directional changes,
you'll want to check the "Use Selection Order" option for the most predictable
results:

<p><video src="../../assets/videos/curve-distribute-between-vertices-selection-order.mp4" controls=true /></p>

## Close the Loop

If you want the curve along which your vertices are distributed to form a
closed loop, you *must* have selected "Use Selection Order", *and* "Close":

<p><video src="../../assets/videos/curve-distribute-between-vertices-selection-order-closed.mp4" controls=true /></p>

## Create a Deformer

If you check "Create Deformer", locators will be created for manipulating
a wire deformer connected to your mesh:

<p><video src="../../assets/videos/curve-distribute-between-vertices-create-deformer.mp4" controls=true /></p>
