1. Introduction

In order to compute optimal x-monotone pixel grid region
that maximize entropy or mutual information, this
"hand-probe" function is necessary.

Read "Chapter 3" for the detail.


2. How to Use This Program

2.1 Test Data Generation

You can make pixel grid region by "MakeMatrix.java".

Issue
javac MakeMatrix.java
to compile.

Issue
java MakeMatrix [xsize] [ysize]
to generate sample 2D matrix with [xsize] X [ysize].
This outputs the matrix data to STDOUT.
So, redirect this to file.

For example, issue
java MakeMatix 20 20 > x.txt
Then, sample matrix is outputed into "x.txt".

Output is like following.

10 10
-4 -2  1  6  4 -6  3  4  8 -2
 0 -0  8  1  5 -5 -6 -1  4  8
-1  0  3  6  1 -6 -10 6 -9  1
 6 -5  8 -9  1  4 -5 -1 -5  5
-1 -2 -1 -5  6  7 -8 -1 10  7
-5 -6 -0 -2  9 -1 -8 10  6 -9
-9  1  9  1 -2 -3 -8  2  3 -1
-8 -8 -9  5 -8  3  0 -9  6  1
-4 -8  4 -6 -2 -4 -4  3 -5 -8
 3  3  7  8 -0 10  8 -0 -6  3

The first line, "10 10", shows x-size and y-size.
Elements of matrix begins from the next line.
Origin is top left side.
In this example,
(0,0) is -4
(1,0) is -2
(2,0) is 1
...
(9,9) is 3


2.2 Inner Product Matrix

You can compute the inner product matrix, i.e., (\Theta,
{\bf x}) from "x.txt".
If the number of class is two,  
just multiply each element in x.txt and theta.


2.3 Hand Probe Function

Issue
javac OptRegion.java
to compile.

Issue
java OptRegion [inner product matrix]
to compute hand-probed region with theta.

For example, issue
java OptRegion g.txt

This outputs the result into STDOUT.
The result is a set of connected vertical intervals.

For example, 

gsum=158.0
xoff=0
[9,9]
[9,9]
[0,9]
[0,2]
[0,5]
[3,9]
[9,9]
[0,9]
[4,7]
[1,4]

shows the region is start from x=0. ("xoff")
In the first column, x=0, 
y-value of the vertical interval is (0,9) to (0,9).
In x=1, y-coord of the vertical interval is (1,9) to (1,9).
In x=2, y-coord of the vertical interval is (2,0) to (2,9).
In x=3, y-coord of the vertical interval is (3,0) to (3,2).
...

Sum of inside the x-monotone region is 158.
