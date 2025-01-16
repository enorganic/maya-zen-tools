# Loft Distribute Vertices Between Edges

## Default Options

With the default options, "Loft Distribute Vertices Between Edges" will
distribute vertices sandwiched between your selected edges along a (dynamically
created and not retained) lofted NURBS surface passing between the edges
you've selected:

<p><video src="../../assets/videos/loft-distribute-vertices-between-edges.mp4" controls=true /></p>

Note: The vertices selected adhere to the same logic as
[Select Edges Between Vertices](selection/select-edges-between-vertices.md).

## Proportional Distributions

The default distribution type for this tool is "Uniform", however you can
select "Proportional" distribution in order to retain the same relative spacing
between redistributed vertices:

<p><video src="../../assets/videos/loft-distribute-vertices-between-edges-proportional.mp4" controls=true /></p>

## Create a Deformer

If you check "Create Deformer", the curves forming the loft will be retained
and connected to a proximity wrap deformer affecting your mesh:

<p><video src="../../assets/videos/curve-distribute-between-vertices-create-deformer.mp4" controls=true /></p>