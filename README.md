# Dream Matrix
A tool made to procedurally generate cities and urban landscapes

Introduction
================
I've built a GPU accelerated monte carlo path tracer using CUDA and C++. The parallelization is happening on a ray-by-ray basis, with the terminated rays being eliminated via stream compaction and sorted by material type in order to avoid warp divergence. The path tracer takes in a scene description .txt file and outputs a rendered image. 
