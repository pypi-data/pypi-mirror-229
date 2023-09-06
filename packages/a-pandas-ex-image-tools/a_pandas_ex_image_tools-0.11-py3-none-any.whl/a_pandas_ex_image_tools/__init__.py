from functools import wraps


def warn(*args, **kwargs):
    pass


import warnings

warnings.warn = warn
import sys

debugger = sys.modules[__name__]
debugger.stop_on_exceptions = True
debugger.print_all_exceptions = False

import numexpr

from collections import defaultdict
import cv2
from a_pandas_ex_obj_into_cell import (
    put_one_object_into_several_cells,
)
from ansi.colour.rgb import rgb256
from ansi.colour import fg, bg, fx
import numpy as np
from a_cv_imwrite_imread_plus import open_image_in_cv
from a_pandas_ex_plode_tool import pd_add_explode_tools
from PrettyColorPrinter import add_printer
from a_pandas_ex_to_tuple import pd_add_tuples
from flexible_partial import FlexiblePartialOwnName

pd_add_tuples()
from flatten_everything import flatten_everything
from shapely.geometry import Polygon
from shapely.ops import unary_union
from a_pandas_ex_enumerate_groups import pd_add_enumerate_group
from sklearn.cluster import DBSCAN

pd_add_enumerate_group()
from a_cv2_imshow_thread import add_imshow_thread_to_cv2

add_imshow_thread_to_cv2()

add_printer()
pd_add_explode_tools()
from a_pandas_ex_column_reduce import pd_add_column_reduce
import pandas as pd

pd_add_column_reduce()
from a_pandas_ex_horizontal_explode import pd_add_horizontal_explode

pd_add_horizontal_explode()

nested_dict = lambda: defaultdict(nested_dict)

from a_pandas_ex_lookupdict import pd_add_lookup_dict, get_lookup_dict

pd_add_lookup_dict()

from a_pandas_ex_obj_into_cell import pd_add_obj_into_cells

pd_add_obj_into_cells()
from a_pandas_ex_closest_color import get_closest_colors
from a_pandas_ex_multiloc import pd_add_multiloc

pd_add_multiloc()


from pandas.core.frame import DataFrame
from PrettyColorPrinter import add_printer

add_printer(True)


pd_add_obj_into_cells()


def ignore_exceptions_decorator(f_py=None, exception_value=None):
    """
    from random import choice

    @ignore_exceptions_decorator(print_exception=True, exception_value=False, disable=False)
    def testest(number):
        if number == 0:
            return True
        elif number == 1:
            print(number / 0)
        return True


    testex = [testest(choice([0, 1])) for x in range(10)]


    division by zero
    division by zero
    testex
    Out[3]: [True, True, False, True, False, True, True, True, True, True]

    https://stackoverflow.com/questions/5929107/decorators-with-parameters

    #Blueprint for other useful stuff
    """
    assert callable(f_py) or f_py is None

    def _decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if debugger.stop_on_exceptions is False:
                try:
                    return func(*args, **kwargs)
                except Exception as fexa:
                    if debugger.print_all_exceptions:
                        print(fexa)
                    return exception_value
            else:
                return func(*args, **kwargs)

        return wrapper

    return _decorator(f_py) if callable(f_py) else _decorator


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def image2df(image):
    isnumpy = False
    try:
        isnumpy = "numpy" == type(image).__module__.lower()
    except Exception as da:
        print(da)
    if isnumpy:
        image = cv2.rotate(cv2.flip(image, -1), cv2.ROTATE_180)
    image = open_image_in_cv(image, bgr_to_rgb=False, channels_in_output=3)
    colourArray = image.reshape(
        (image.shape[0] * image.shape[1], image.shape[2])
    ).reshape(image.shape[:-1][::-1] + (3,))
    indicesArray = np.moveaxis(np.indices(image.shape[:-1]), 0, 2).reshape(
        (*image.shape[:-1][::-1], 2)
    )
    allArray = np.dstack((indicesArray, colourArray)).reshape((-1, 5))
    df2 = pd.DataFrame(allArray, columns=["y", "x", "red", "green", "blue"]).copy()
    if not df2.empty:
        df2["x"] = df2["x"].astype(np.uint16)
        df2["y"] = df2["y"].astype(np.uint16)

        if "red" in df2.columns:
            df2["red"] = df2["red"].astype(np.uint8)
        if "green" in df2.columns:
            df2["green"] = df2["green"].astype(np.uint8)
        if "blue" in df2.columns:
            df2["blue"] = df2["blue"].astype(np.uint8)
        df2["red"], df2["blue"] = df2["blue"], df2["red"]
        df2 = df2.filter(["x", "y", "red", "green", "blue"])
    return df2


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(
        columns=["pic_index", "x", "y", "r1", "g1", "b1", "r2", "g2", "b2"]
    ),
)
def compare_2_df_pictures(df, df2):
    if not isinstance(df, pd.DataFrame):
        df = image2df(df)
    if not isinstance(df2, pd.DataFrame):
        df2 = image2df(df2)
    df3 = df.compare(df2).index
    subresult = (
        pd.concat([df.loc[df3], df2.loc[df3]], axis=1, ignore_index=True)
        .drop(columns=[5, 6])
        .rename(
            columns={
                0: "x",
                1: "y",
                2: "r1",
                3: "g1",
                4: "b1",
                7: "r2",
                8: "g2",
                9: "b2",
            }
        )
        .reset_index()
        .rename(columns={"index": "pic_index"})
    )
    return subresult


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def convert_x_y_column_to_cv2_coords(df):
    return df[["x", "y"]].__array__().reshape((1, -1, 2)).astype(int)


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def cv2_convex_hull(df):
    return cv2.convexHull(convert_x_y_column_to_cv2_coords(df))


@ignore_exceptions_decorator(
    exception_value=Polygon(),
)
def cv2_convex_hull_coords_to_shapely(convex_hull_coords):
    return Polygon(convex_hull_coords.reshape((-1, 2)))


@ignore_exceptions_decorator(
    exception_value=Polygon(),
)
def cv2_xy_coords_to_shapely(df):
    convex_hull_coords = cv2_convex_hull(df)
    return Polygon(convex_hull_coords.reshape((-1, 2)))


@ignore_exceptions_decorator(
    exception_value=list(),
)
def get_shapely_bounds_as_tuple(polygon):
    return [int(x) for x in polygon.boundary.bounds]


@ignore_exceptions_decorator(
    exception_value=tuple(),
)
def tuple_with_4_to_2_tuples(coords):
    return tuple(coords[:2]), tuple(coords[2:])


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def draw_rectangle_cv2(
    image,
    start,
    end,
    color=(0, 0, 255),
    outlinecolor=(0, 0, 0),
    outlineborder=2,
    thickness=2,
):
    imi = open_image_in_cv(image, channels_in_output=3).copy()
    imi = cv2.rectangle(
        imi,
        start,
        end,
        outlinecolor,
        outlineborder,
    )

    imi = cv2.rectangle(
        imi,
        start,
        end,
        color,
        thickness,
    )
    return imi


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def multicolor_lookup(df, colorlist):
    if len(colorlist) <= 9:
        try:
            return multicolor_search_steroids(df, colorlist)
        except Exception as fe:
            print(fe)
            raise fe
            pass
    return df.d_multiloc(
        column_and_values=[
            (
                "==",
                ("red", "green", "blue"),
                colorlist,
            )
        ],
        print_query=False,
    )


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def multicolor_search_steroids(df, colors):
    colorstosearch = colors
    red = df.red.__array__()
    green = df.green.__array__()
    blue = df.blue.__array__()
    wholedict = {"blue": blue, "green": green, "red": red}
    wholecommand = ""
    for ini, co in enumerate(colorstosearch):
        for ini2, col in enumerate(co):
            wholedict[f"varall{ini}_{ini2}"] = np.array([col]).astype(np.uint8)
        wholecommand += f"((red == varall{ini}_0) & (green == varall{ini}_1) & (blue == varall{ini}_2))|"
    wholecommand = wholecommand.strip("|")
    expre = numexpr.evaluate(wholecommand, local_dict=wholedict)
    return df.loc[expre]


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def singlecolor_lookup(df, color):
    try:
        return multicolor_search_steroids(df, [color])
    except Exception as fe:
        print(fe)
    if "red" in df.columns:
        return df.loc[
            (df.red == color[0]) & (df.green == color[1]) & (df.blue == color[2])
        ]
    return df.loc[(df.r == color[0]) & (df.g == color[1]) & (df.b == color[2])]


@ignore_exceptions_decorator(
    exception_value=dict(),
)
def get_color_lookup_dict(df):
    return get_lookup_dict(
        df=df, as_values=["x", "y"], as_index=["red", "green", "blue"]
    )


@ignore_exceptions_decorator(
    exception_value=list(),
)
def get_whole_area(df):
    return [
        (
            int(df["x"].min()),
            int(df["y"].min()),
            int(df["x"].max()) + 1,
            int(df["y"].max()) + 1,
        )
    ]


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(
        columns=[
            "red",
            "green",
            "blue",
            "qty",
            "size_of_area",
            "percentage_of_area",
            "region",
        ]
    ),
)
def get_colors_in_regions_and_count_qty(df, regions=None, with_rgb_tuple_column=False):
    if not regions:
        regions = get_whole_area(df)
    areas = regions
    resas = []
    for reci in areas:
        if (
            not isinstance(reci[0], int)
            and not isinstance(reci[1], int)
            and not isinstance(reci[2], int)
            and not isinstance(reci[3], int)
        ):
            continue
        area_size = (reci[2] - reci[0]) * (reci[3] - reci[1])
        allco = (
            df.loc[
                (
                    (df["x"] >= reci[0])
                    & (df["x"] <= reci[2])
                    & (df["y"] >= reci[1])
                    & (df["y"] <= reci[3])
                )
            ]
            .value_counts(["red", "green", "blue"])
            .reset_index()
            .rename(columns={'count': "qty"})
            .copy()
        )
        allco["size_of_area"] = area_size
        allco["percentage_of_area"] = allco["qty"] / area_size * 100
        allco = put_one_object_into_several_cells(
            dframe=allco,
            column="region",
            value=reci,
            indexlist=None,
            ffill=True,
            bfill=True,
        )
        resas.append(allco.copy())
    iuia = pd.concat(resas, ignore_index=True).copy()
    if with_rgb_tuple_column:
        tua = tuple(
            iuia[["red", "green", "blue"]].ds_to_tuples(index=False, columns=False)
        )
        iuia = iuia.d_list_items_to_cells(column="color", values=tua)
    return iuia


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def cluster_coordinates(coords, eps=2, min_samples=4, n_jobs=-1, **kwargs):
    clustering = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=n_jobs, **kwargs).fit(
        coords
    )
    uniquelabels = np.unique(clustering.labels_)
    allresis = [
        coords[np.where(clustering.labels_ == u)] for u in uniquelabels if u != -1
    ]
    return allresis


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def get_xy_from_df(df):
    return df[["x", "y"]].__array__()


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(
        columns=[
            "aa_repr_point",
            "aa_bounds",
            "aa_polygon",
            "aa_area",
            "aa_all_coords",
            "aa_convexhull",
            "aa_convexhull_squeezed",
            "aa_draw_poly",
            "aa_draw_rectangle",
        ]
    ),
)
def get_color_clusters(
    coordinates,
    eps=2,
    min_samples=4,
    n_jobs=-1,
    poly_color=(255, 255, 0),
    poly_outline_thickness=3,
    rectanglecolor=(0, 255, 0),
):
    if isinstance(coordinates, pd.DataFrame):
        readycoords = get_xy_from_df(coordinates)
    else:
        readycoords = coordinates
    clu = cluster_coordinates(
        coords=readycoords, eps=eps, min_samples=min_samples, n_jobs=n_jobs
    )
    allfound = []
    for c in clu:
        convexh = None
        convexhsquee = None
        poo = None
        repr_point = None
        bou = None
        drawpoly = None
        drawrec = None
        area = None
        try:
            convexh = cv2.convexHull(c.reshape((1, -1, 2)).astype(int))
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:

            convexhsquee = np.squeeze(convexh)
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:

            poo = Polygon(convexhsquee)
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:

            area = poo.area
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)

        try:
            repr_point = tuple(
                [
                    int(x)
                    for x in flatten_everything(poo.representative_point().coords.xy)
                ]
            )
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:
            bou = tuple(get_shapely_bounds_as_tuple(poo))
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:
            drawpoly = FlexiblePartialOwnName(
                cv2.polylines,
                "()",
                False,
                np.array([convexhsquee]),
                True,
                list(reversed(poly_color)),
                poly_outline_thickness,
            )
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        try:

            drawrec = FlexiblePartialOwnName(
                cv2.rectangle,
                "()",
                False,
                list(bou[:2]),
                list(bou[2:4]),
                list(reversed(rectanglecolor)),
                -1,
            )
        except Exception as fe:
            if debugger.print_all_exceptions:
                print(fe)
        varas = (
            repr_point,
            bou,
            poo,
            area,
            c,
            convexh,
            convexhsquee,
            drawpoly,
            drawrec,
        )
        allfound.append(varas)
    dfframe = pd.DataFrame(allfound, dtype="object")
    dfframe.columns = [
        "aa_repr_point",
        "aa_bounds",
        "aa_polygon",
        "aa_area",
        "aa_all_coords",
        "aa_convexhull",
        "aa_convexhull_squeezed",
        "aa_draw_poly",
        "aa_draw_rectangle",
    ]

    return dfframe


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(
        columns=[
            "aa_repr_point",
            "aa_bounds",
            "aa_polygon",
            "aa_area",
            "aa_all_coords",
            "aa_convexhull",
            "aa_convexhull_squeezed",
            "aa_draw_poly",
            "aa_draw_rectangle",
            "aa_merged_poly",
            "aa_merged_poly_bounds",
            "aa_merged_poly_area",
            "aa_merged_poly_repr_point",
            "bb_pic_merged",
            "bb_pic",
        ]
    ),
)
def get_and_merge_color_clusters(
    coordinates,
    image=None,
    show_results=False,
    max_merge_distance=2,
    eps=2,
    min_samples=4,
    n_jobs=-1,
    poly_color=(255, 255, 0),
    poly_outline_thickness=3,
    rectanglecolor=(0, 255, 0),
    mergedcolor=(0, 0, 255),
):
    imi = None
    img_resize = None
    colclu = get_color_clusters(
        coordinates,
        eps=eps,
        min_samples=min_samples,
        n_jobs=n_jobs,
        poly_color=poly_color,
        poly_outline_thickness=poly_outline_thickness,
        rectanglecolor=rectanglecolor,
    )

    if not isinstance(image, type(None)):
        img_resize = open_image_in_cv(image, channels_in_output=3).copy()
        colclu.aa_draw_rectangle.dropna().apply(lambda x: x(img_resize))
        colclu.aa_draw_poly.dropna().apply(lambda x: x(img_resize))

    joinedcol = colclu["aa_polygon"].s_column_reduce(
        expression=f"func([x,y]) if x.distance(y) < {max_merge_distance} else x",
        func=unary_union,
        own_value_against_own_value=True,
        ignore_exceptions=True,
        print_exceptions=debugger.print_all_exceptions,
    )

    joinedcol = joinedcol.s_column_reduce_update(
        expression=f"func([x,y]) if x.distance(y) < {max_merge_distance} else x",
        func=unary_union,
        own_value_against_own_value=True,
        ignore_exceptions=True,
        print_exceptions=debugger.print_all_exceptions,
    )
    if not isinstance(image, type(None)):

        imi = open_image_in_cv(image, channels_in_output=3).copy()
        joinedcol.dropna().apply(
            lambda x: tuple_with_4_to_2_tuples(get_shapely_bounds_as_tuple(x))
        ).drop_duplicates().apply(
            lambda y: cv2.rectangle(
                imi,
                y[0],
                y[1],
                list(reversed(mergedcolor)),
                -1,
            )
        )
    if (
        show_results
        and not isinstance(imi, type(None))
        and not isinstance(img_resize, type(None))
    ):
        cv2.imshow_thread([imi, img_resize])
    colclu = (
        pd.concat([colclu, joinedcol], axis=1)
        .rename(columns={0: "aa_merged_poly"})
        .copy()
    )
    colclu["aa_merged_poly_bounds"] = colclu.aa_merged_poly.apply(
        lambda x: ignore_exceptions_decorator(
            lambda: tuple_with_4_to_2_tuples(get_shapely_bounds_as_tuple(x)),
            exception_value=pd.NA,
        )()
    )
    colclu["aa_merged_poly_area"] = colclu.aa_merged_poly.apply(
        lambda x: ignore_exceptions_decorator(
            lambda: x.area,
            exception_value=pd.NA,
        )()
    )
    colclu["aa_merged_poly_repr_point"] = colclu.aa_merged_poly.apply(
        lambda x: ignore_exceptions_decorator(
            lambda: tuple(
                int(o) for o in flatten_everything(x.representative_point().coords.xy)
            ),
            exception_value=pd.NA,
        )()
    )
    colclu = colclu.d_one_object_to_several_cells(
        column="bb_pic_merged",
        value=imi,
        indexlist=None,
        ffill=True,
        bfill=True,
    )
    colclu = colclu.d_one_object_to_several_cells(
        column="bb_pic",
        value=img_resize,
        indexlist=None,
        ffill=True,
        bfill=True,
    )

    return colclu


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def limit_search_areas(df, areas):
    query = ""

    for reci in areas:
        if (
            not isinstance(reci[0], int)
            and not isinstance(reci[1], int)
            and not isinstance(reci[2], int)
            and not isinstance(reci[3], int)
        ):
            continue
        query += f"""((df["x"] >= {reci[0]}) & (df["x"] <= {reci[2]}) & (df["y"] >= {reci[1]}) & (df["y"] <= {reci[3]}))|"""
    query = query.rstrip("|")
    return df.loc[eval(query)]


def print_full_col(text, colour):
    return "".join(
        list(
            map(
                str,
                (
                    fx.bold,
                    bg.brightwhite,
                    fg.brightwhite,
                    rgb256(colour[0], colour[1], colour[2]),
                    text,
                    bg.brightwhite,
                    fg.brightwhite,
                    fx.bold,
                    fx.reset,
                ),
            )
        )
    )


@ignore_exceptions_decorator(exception_value=None)
def print_colors_in_image(df, end=100):
    df2 = get_colors_in_regions_and_count_qty(
        df, regions=None, with_rgb_tuple_column=False
    )
    for li in (
        df2[:end]
        .apply(
            lambda x: print_full_col(
                str((x["red"], x["green"], x["blue"])).rjust(20),
                (x["red"], x["green"], x["blue"]),
            )
            + "      "
            + print_full_col("████████", (x["red"], x["green"], x["blue"]))
            + str((x["red"], x["green"], x["blue"])).rjust(20)
            + str(x["qty"]).rjust(10),
            axis=1,
        )
        .to_list()
    ):
        print(li)

    # return df


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["r", "g", "b", "rating", "rgb"]),
)
def find_closest_colors(df, colorlist):
    co = (
        df[["red", "green", "blue"]]
        .value_counts()
        .reset_index()
        .drop(columns=0)
        .astype(np.uint8)
        .__array__()
    )

    return get_closest_colors(colorlist, colorlist=co)


@ignore_exceptions_decorator(
    exception_value=[],
)
def get_list_of_all_colors_in_range(start, end):
    allco = []
    allrgbvals = []
    for s, e in zip(start, end):
        allrgbvals.append(tuple(range(s, e + 1)))
    for r in allrgbvals[0]:
        for g in allrgbvals[1]:
            for b in allrgbvals[2]:
                allco.append((r, g, b))
    return allco


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def get_coords_of_colors_in_region(df, colordict):
    wholequery = ""
    for key, item in colordict.items():
        for ar_ in item:
            qu = f'(df["red"] == {key[0]})&(df["green"] == {key[1]})&(df["blue"] == {key[2]})&(df["x"] >= {ar_[0]})&(df["x"] <= {ar_[2]})&(df["y"] >= {ar_[1]})&(df["y"] <=  {ar_[3]})|'
            wholequery = wholequery + qu
    wholequery = wholequery.rstrip("|")
    return df.loc[eval(wholequery)]


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["red", "green", "blue"]),
)
def x_y_as_index(df):
    index = pd.MultiIndex.from_arrays(
        [df["x"].__array__(), df["y"].__array__()], names=("x", "y")
    )
    df2 = df.set_index(index).drop(columns=["y", "x"]).sort_index()
    return df2


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["red", "green", "blue"]),
)
def get_colors_of_coords(dframe, coordlist):
    aro = x_y_as_index(dframe)
    return aro.loc[coordlist]


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y"]),
)
def r_g_b_as_index(df2):
    index = pd.MultiIndex.from_arrays(
        [df2.red.__array__(), df2.green.__array__(), df2.blue.__array__()],
        names=("red", "green", "blue"),
    )
    return df2.set_index(index).drop(columns=["red", "green", "blue"]).sort_index()


@ignore_exceptions_decorator(
    exception_value=None,
)
def get_average_rgb(df):
    return (df[["red", "green", "blue"]].sum() / len(df)).astype(int).to_list()


@ignore_exceptions_decorator(
    exception_value=np.array([]),
)
def df_to_image(df):
    maxlen = df.y.max()
    blue = np.array(np.array_split(df.blue.to_numpy(), maxlen + 1))
    green = np.array(np.array_split(df.green.to_numpy(), maxlen + 1))
    red = np.array(np.array_split(df.red.to_numpy(), maxlen + 1))
    convertedimage = np.dstack((blue, green, red))
    return convertedimage


def df_imshow(df):
    bi = df_to_image(df)
    cv2.imshow_thread(bi)
    return df


def _get_unique_colors_in_region(df, regions, unique):
    first = df.im_limit_search_areas(regions)  # .drop(columns=['x', 'y'])
    second = df.loc[set(df.index) - set(first.index)]  # .drop(columns=['x', 'y'])
    isthere = first.loc[
        first[["red", "green", "blue"]]
        .agg(tuple, 1)
        .isin(second[["red", "green", "blue"]].agg(tuple, 1))
    ]
    if not unique:
        return isthere
    isnotthere = first.loc[set(first.index) - set(isthere.index)]
    return isnotthere


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def get_unique_colors_in_region(df, regions):
    return _get_unique_colors_in_region(df, regions, unique=True)


@ignore_exceptions_decorator(
    exception_value=pd.DataFrame(columns=["x", "y", "red", "green", "blue"]),
)
def get_not_unique_colors_in_region(df, regions):
    return _get_unique_colors_in_region(df, regions, unique=False)


def pd_add_image_tools():
    pd.Q_image2df = image2df
    DataFrame.im_compare_2_images = compare_2_df_pictures
    DataFrame.im_xy_to_cv2_coords = convert_x_y_column_to_cv2_coords
    DataFrame.im_xy_to_convex_hull = cv2_convex_hull
    DataFrame.im_xy_to_shapely = cv2_xy_coords_to_shapely
    DataFrame.im_xy_to_np = get_xy_from_df
    DataFrame.im_xy_to_color_clusters = get_color_clusters
    DataFrame.im_xy_to_merged_color_clusters = get_and_merge_color_clusters

    DataFrame.im_multicolor_lookup = multicolor_lookup
    DataFrame.im_singlecolor_lookup = singlecolor_lookup
    DataFrame.im_get_color_lookup_dict = get_color_lookup_dict
    DataFrame.im_get_image_size = get_whole_area
    DataFrame.im_get_colors_in_regions_and_count = get_colors_in_regions_and_count_qty
    DataFrame.im_limit_search_areas = limit_search_areas
    DataFrame.im_print_all_colors = print_colors_in_image
    DataFrame.im_get_closest_colors = find_closest_colors
    DataFrame.im_get_coords_of_colors_in_regions = get_coords_of_colors_in_region
    DataFrame.im_xy_as_index = x_y_as_index
    DataFrame.im_rgb_as_index = r_g_b_as_index
    DataFrame.im_get_colors_of_coords = get_colors_of_coords
    DataFrame.im_get_average_rgb = get_average_rgb
    DataFrame.im_df_to_np_image = df_to_image
    DataFrame.im_show_df_image = df_imshow
    DataFrame.im_get_unique_colors_in_region = get_unique_colors_in_region
    DataFrame.im_get_not_unique_colors_in_region = get_not_unique_colors_in_region
