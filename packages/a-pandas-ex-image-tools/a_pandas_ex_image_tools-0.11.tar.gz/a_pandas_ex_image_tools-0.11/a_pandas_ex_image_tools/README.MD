```python
$pip install a-pandas-ex-image-tools
import cv2
import pandas as pd

from a_cv2_imshow_thread import add_imshow_thread_to_cv2
add_imshow_thread_to_cv2()

from a_pandas_ex_image_tools import pd_add_image_tools, debugger, get_list_of_all_colors_in_range

pd_add_image_tools()
#you can ignore all exceptions
debugger.stop_on_exceptions = True

#Useful if you want to ignore every exception, but want to see what's going on
debugger.print_all_exceptions = True

pythonlogo = 'https://github.com/hansalemaos/screenshots/raw/main/colorfind1.png'


```


<img src="https://github.com/hansalemaos/screenshots/raw/main/colorfind1.png"/>



```python
df = pd.Q_image2df(pythonlogo)
df
Out[5]: 
         x    y  red  green  blue
0        0    0    0      0     0
1        1    0    0      0     0
2        2    0    0      0     0
3        3    0    0      0     0
4        4    0    0      0     0
    ...  ...  ...    ...   ...
39995  195  199    0      0     0
39996  196  199    0      0     0
39997  197  199    0      0     0
39998  198  199    0      0     0
39999  199  199    0      0     0
[40000 rows x 5 columns]
```



```python
df1 = df.im_multicolor_lookup([(255, 232, 115)])
df1
Out[11]: 
         x    y  red  green  blue
13337  137   66  255    232   115
13338  138   66  255    232   115
13339  139   66  255    232   115
13340  140   66  255    232   115
13341  141   66  255    232   115
    ...  ...  ...    ...   ...
25269   69  126  255    232   115
25270   70  126  255    232   115
25467   67  127  255    232   115
25468   68  127  255    232   115
25667   67  128  255    232   115
[608 rows x 5 columns]
```



```python
df1.im_xy_to_convex_hull()  # get the convex hull 
Out[12]: 
array([[[154,  67]],
       [[153,  68]],
       [[ 73, 124]],
       [[ 67, 128]],
       [[ 67, 114]],
       [[ 70, 108]],
       [[ 74, 104]],
       [[137,  66]],
       [[150,  66]]], dtype=int32)
```



```python
df.im_show_df_image()  # cv2.imshow
```



```python
# converts the pandas DataFrame back to a numpy array
df.im_df_to_np_image()  
```



```python
df.im_print_all_colors()  # prints all colors sorted by qty
```



```python
df1.im_xy_to_shapely()
Out[13]: <shapely.geometry.polygon.Polygon at 0x21302f70>
```



```python
# Gets all x,y coordinates as a numpy array
df1.im_xy_to_np()
Out[14]: 
array([[137,  66],
       [138,  66],
       [139,  66],
       ...,
       [ 67, 127],
       [ 68, 127],
       [ 67, 128]], dtype=uint16)
```



```python
# you can even edit images 
df.loc[df.im_multicolor_lookup([(0,0,0)]).index, ['red', 'green', 'blue']] = [255,255,0] 
```



<img src="https://github.com/hansalemaos/screenshots/raw/main/2022-12-27%2003_40_27-.png"/>






```python
# Replace a color range with one color
df.loc[df.im_multicolor_lookup(get_list_of_all_colors_in_range((0,0,0), (10,10,10))).index, ['red', 'green', 'blue']] = [255,255,0] 
```



```python
# cluster colors in areas
# More about the parameters: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.DBSCAN.html
multilookupdf = df.im_multicolor_lookup(
    colorlist=[(255, 232, 115), (255, 0, 0), (48, 105, 152)], ).im_xy_to_color_clusters(eps=2, min_samples=4, n_jobs=-1,
    poly_color=(255, 255, 0), poly_outline_thickness=3, rectanglecolor=(0, 255, 0), )
multilookupdf
Out[24]: 
  aa_repr_point             aa_bounds  ... aa_draw_poly aa_draw_rectangle
0     (124, 82)    (106, 66, 132, 96)  ...           ()                ()
1     (142, 71)    (137, 66, 154, 79)  ...           ()                ()
2     (73, 119)   (67, 102, 104, 128)  ...           ()                ()
3    (158, 123)  (144, 117, 164, 131)  ...           ()                ()
4    (119, 155)   (93, 139, 132, 167)  ...           ()                ()
[5 rows x 9 columns]
```



```python
# Cluster multiple colors
multilookupdf = df.im_multicolor_lookup(
    colorlist=[(255, 232, 115), (255, 0, 0), (48, 105, 152)], ).im_xy_to_color_clusters(eps=2, min_samples=4, n_jobs=-1,
    poly_color=(255, 0, 120), poly_outline_thickness=3, rectanglecolor=(0, 255, 0), )
```



```python
# show the clustered results
npimage = df.im_df_to_np_image().copy()
multilookupdf.aa_draw_rectangle.apply(lambda x: x(npimage))
multilookupdf.aa_draw_poly.apply(lambda x: x(npimage))
cv2.imshow_thread(npimage)
```



<img src="https://github.com/hansalemaos/screenshots/raw/main/2022-12-27%2003_49_27-.png"/>





```python
bab=df.im_multicolor_lookup(colorlist=[(255, 232, 115), (48, 105, 152)], ).im_xy_to_merged_color_clusters(
    image=df.im_df_to_np_image().copy(), show_results=True, max_merge_distance=2, eps=2, min_samples=4, n_jobs=-1,
    poly_color=(255, 255, 0), poly_outline_thickness=3, rectanglecolor=(0, 255, 0), mergedcolor=(0, 0, 255), )


bab
Out[6]: 
  aa_repr_point  ...                                             bb_pic
0     (124, 82)  ...  [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...
1     (142, 71)  ...  [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...
2     (73, 119)  ...  [[[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], ...
```



<img src="https://github.com/hansalemaos/screenshots/raw/main/2022-12-27%2004_02_09-.png"/>





<img src="https://github.com/hansalemaos/screenshots/raw/main/2022-12-27%2004_01_57-.png"/>




```python
# Do you prefer working with dicts instead of DataFrames? 
df.im_get_color_lookup_dict()
{(0,
  0,
  0): array([[  0,   0],
        [  1,   0],
        [  2,   0],
        ...,
        [196, 199],
        [197, 199],
        [198, 199]], dtype=uint16),
 (15, 33, 48): array([[199, 199]], dtype=uint16),
 (17, 35, 49): array([[131,  88]], dtype=uint16),
 (17, 35, 50): array([[ 63, 114]], dtype=uint16),
 (17, 36, 53): array([[75, 99]], dtype=uint16),
 (17,
  37,
  53): array([[119,  97],
        [129,  91]], dtype=uint16),
 (18, 36, 50): array([[126,  94]], dtype=uint16),
 (18, 37, 52): array([[125,  35]], dtype=uint16),
 (19, 38, 53): array([[ 68, 104]], dtype=uint16),
 (19,
  39,
  55): array([[ 36, 124],
        [ 73, 100]], dtype=uint16),
...
```



```python
df.im_get_image_size()
# Out[7]: [(0, 0, 200, 200)]
```



```python
# Count colors in certain regions
df.im_get_colors_in_regions_and_count(regions=[(10, 10, 100, 100), (150, 150, 160, 170)])
Out[11]: 
     red  green  blue  ...  size_of_area  percentage_of_area                region
0      0      0     0  ...          8100           61.925926    (10, 10, 100, 100)
1     69    132   182  ...          8100            1.790123    (10, 10, 100, 100)
2    255    255   255  ...          8100            1.160494    (10, 10, 100, 100)
3     67    129   179  ...          8100            1.148148    (10, 10, 100, 100)
4     62    123   172  ...          8100            1.135802    (10, 10, 100, 100)
..   ...    ...   ...  ...           ...                 ...                   ...
218   59    110   151  ...          8100            0.012346    (10, 10, 100, 100)
219   59    111   153  ...          8100            0.012346    (10, 10, 100, 100)
220   60    112   154  ...          8100            0.012346    (10, 10, 100, 100)
221   62    111   147  ...          8100            0.012346    (10, 10, 100, 100)
222    0      0     0  ...           200          115.500000  (150, 150, 160, 170)
[223 rows x 7 columns]
```



```python
# You can limit the search region
df.im_limit_search_areas(areas=[(0, 0, 50, 50), (50, 50, 150, 170)]).im_multicolor_lookup(
    colorlist=[(255, 232, 115), (255, 0, 0), (48, 105, 152)])
Out[12]: 
         x    y  red  green  blue
13332  132   66   48    105   152
13337  137   66  255    232   115
13338  138   66  255    232   115
13339  139   66  255    232   115
13340  140   66  255    232   115
    ...  ...  ...    ...   ...
33502  102  167  255      0     0
33503  103  167  255      0     0
33504  104  167  255      0     0
33505  105  167  255      0     0
33506  106  167  255      0     0
[1352 rows x 5 columns]
```



```python
# define regions for every individual color
colordict = {(255, 0, 0): [(0, 0, 50, 50), (0, 0, 1000, 1000)],
    (255, 232, 115): [(0, 0, 1000, 1000), (500, 500, 502, 502), (900, 900, 1000, 950), ],
    (255, 255, 255): [(0, 0, 1000, 1000), (400, 200, 800, 400)], (0, 176, 111): [(0, 0, 1000, 1000)],
    (57, 59, 61): [(0, 0, 1000, 1000)], (0, 0, 0): [(0, 0, 1000, 1000)], }
regi = df.im_get_coords_of_colors_in_regions(colordict)

         x    y  red  green  blue
0        0    0    0      0     0
1        1    0    0      0     0
2        2    0    0      0     0
3        3    0    0      0     0
4        4    0    0      0     0
    ...  ...  ...    ...   ...
39995  195  199    0      0     0
39996  196  199    0      0     0
39997  197  199    0      0     0
39998  198  199    0      0     0
39999  199  199    0      0     0
[28789 rows x 5 columns]
```



```python
# You can use a multi index to check individual pixels 
dfxy = df.im_xy_as_index()

         red  green  blue
x   y                    
0   0      0      0     0
    1      0      0     0
    2      0      0     0
    3      0      0     0
    4      0      0     0
      ...    ...   ...
199 195    0      0     0
    196    0      0     0
    197    0      0     0
    198    0      0     0
    199    0      0     0
[40000 rows x 3 columns]

# Let's get the RGB values using the DataFrame we have just created
dfxy.loc[[(0,100), (100,100), (44,40)]]

Out[17]: 
         red  green  blue
x   y                    
0   100    0      0     0
100 100    0      0     0
44  40     0      0     0
```



```python
# can also be done like that:
coordlist = [(10, 10), (100, 100), (50, 80)]
colors_of_coords = df.im_get_colors_of_coords(coordlist)
colors_of_coords
Out[19]: 
         red  green  blue
x   y                    
10  10     0      0     0
100 100    0      0     0
50  80    70    134   184
```



```python
Compare 2 images:
pythonlogo = 'https://github.com/hansalemaos/screenshots/raw/main/colorfind1.png'
df = pd.Q_image2df(pythonlogo)
df.loc[df.im_multicolor_lookup(get_list_of_all_colors_in_range((0,0,0), (10,10,10))).index, ['red', 'green', 'blue']] = [255,255,0] 
pythonlogo = 'https://github.com/hansalemaos/screenshots/raw/main/colorfind1.png'
df2 = pd.Q_image2df(pythonlogo)
df2.im_compare_2_images(df)
Out[23]: 
       pic_index    x    y  r1  g1  b1   r2   g2  b2
0              0    0    0   0   0   0  255  255   0
1              1    1    0   0   0   0  255  255   0
2              2    2    0   0   0   0  255  255   0
3              3    3    0   0   0   0  255  255   0
4              4    4    0   0   0   0  255  255   0
          ...  ...  ...  ..  ..  ..  ...  ...  ..
27510      39995  195  199   0   0   0  255  255   0
27511      39996  196  199   0   0   0  255  255   0
27512      39997  197  199   0   0   0  255  255   0
27513      39998  198  199   0   0   0  255  255   0
27514      39999  199  199   0   0   0  255  255   0
[27515 rows x 9 columns]
```


```python
# If you want to do additional stuff with OpenCV:
df.im_xy_to_cv2_coords()
Out[28]: 
array([[[  0,   0],
        [  1,   0],
        [  2,   0],
        ...,
        [197, 199],
        [198, 199],
        [199, 199]]])
```



```python
df.im_singlecolor_lookup((255,255,0))
Out[45]: 
         x    y  red  green  blue
0        0    0  255    255     0
1        1    0  255    255     0
2        2    0  255    255     0
3        3    0  255    255     0
4        4    0  255    255     0
    ...  ...  ...    ...   ...
39995  195  199  255    255     0
39996  196  199  255    255     0
39997  197  199  255    255     0
39998  198  199  255    255     0
39999  199  199  255    255     0
[27515 rows x 5 columns]
```



```python
df.im_get_closest_colors([(10,3,4)])
Out[55]: 
       r    g    b      rating         rgb
0      0    0    0   11.179688  (10, 3, 4)
1     15   33   48   53.500000  (10, 3, 4)
2     17   35   49   55.656250  (10, 3, 4)
3     17   35   50   56.468750  (10, 3, 4)
4     18   36   50   57.187500  (10, 3, 4)
..   ...  ...  ...         ...         ...
712  250  242  218  400.750000  (10, 3, 4)
713  252  247  230  411.250000  (10, 3, 4)
714  241  244  246  412.250000  (10, 3, 4)
715  253  251  243  421.500000  (10, 3, 4)
716  255  255  255  432.000000  (10, 3, 4)
[717 rows x 5 columns]
```



```python
get_list_of_all_colors_in_range((0,0,0), (3,4,3))

Out[59]: 
[(0, 0, 0),
 (0, 0, 1),
 (0, 0, 2),
 (0, 0, 3),
 (0, 1, 0),
 (0, 1, 1),
 (0, 1, 2),
 (0, 1, 3),
 (0, 2, 0),
 (0, 2, 1),
 (0, 2, 2),
 (0, 2, 3),
 (0, 3, 0),
```




```python
dfr = df.im_rgb_as_index()
Out[65]: 
                  x    y
red green blue          
0   0     0       0    0
          0       1    0
          0       2    0
          0       3    0
          0       4    0
             ...  ...
255 255   255   120  155
          255   121  155
          255   117  156
          255   118  156
          255   119  156
[40000 rows x 2 columns]


#Now you can use dfr.loc to get the coordinates
dfr.loc[(17,37,53)]
dfr.loc[ (39,83,119)]
```



```python
# finds all colors that only exist in the region and nowhere else in the picture 
df.im_get_unique_colors_in_region([(0,0,100,100)])
Out[72]: 
        x   y  red  green  blue
18432  32  92   73    137   188
18433  33  92   73    137   187
18434  34  92   72    136   187
18435  35  92   72    136   186
18436  36  92   72    135   186
    ..  ..  ...    ...   ...
14255  55  71   71    135   186
14256  56  71   71    135   185
14257  57  71   71    134   185
12266  66  61   53    102   140
18431  31  92   59    111   153
[845 rows x 5 columns]
```

```python
# finds all colors that are in the region and somewhere else in the picture 
df.im_get_not_unique_colors_in_region([(0,0,100,100)])
Out[73]: 
         x    y  red  green  blue
0        0    0    0      0     0
1        1    0    0      0     0
2        2    0    0      0     0
3        3    0    0      0     0
4        4    0    0      0     0
    ...  ...  ...    ...   ...
20096   96  100    0      0     0
20097   97  100    0      0     0
20098   98  100    0      0     0
20099   99  100    0      0     0
20100  100  100    0      0     0
[9356 rows x 5 columns]
```

