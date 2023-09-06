from setuptools import setup, find_packages
import codecs
import os
# 
here = os.path.abspath(os.path.dirname(__file__))
# 
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'README.md'), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()\

from pathlib import Path
this_directory = Path(__file__).parent
#long_description = (this_directory / "README.md").read_text()

VERSION = '''0.11'''
DESCRIPTION = '''Uses pandas/numpy/numexpr for operations on pictures - very fast'''

# Setting up
setup(
    name="a_pandas_ex_image_tools",
    version=VERSION,
    license='MIT',
    url = 'https://github.com/hansalemaos/a_pandas_ex_image_tools',
    author="Johannes Fischer",
    author_email="aulasparticularesdealemaosp@gmail.com",
    description=DESCRIPTION,
long_description = long_description,
long_description_content_type="text/markdown",
    #packages=['PrettyColorPrinter', 'Shapely', 'a_cv2_imshow_thread', 'a_cv_imwrite_imread_plus', 'a_pandas_ex_closest_color', 'a_pandas_ex_column_reduce', 'a_pandas_ex_enumerate_groups', 'a_pandas_ex_horizontal_explode', 'a_pandas_ex_lookupdict', 'a_pandas_ex_multiloc', 'a_pandas_ex_obj_into_cell', 'a_pandas_ex_plode_tool', 'a_pandas_ex_to_tuple', 'ansi', 'flatten_everything', 'flexible_partial', 'numexpr', 'numpy', 'opencv_python', 'pandas', 'scikit_learn'],
    keywords=['pandas', 'OpenCV', 'cv2', 'images', 'pixels', 'detection'],
    classifiers=['Development Status :: 4 - Beta', 'Programming Language :: Python :: 3 :: Only', 'Programming Language :: Python :: 3.10', 'Topic :: Software Development :: Libraries :: Python Modules', 'Topic :: Utilities'],
    install_requires=['PrettyColorPrinter', 'Shapely', 'a_cv2_imshow_thread', 'a_cv_imwrite_imread_plus', 'a_pandas_ex_closest_color', 'a_pandas_ex_column_reduce', 'a_pandas_ex_enumerate_groups', 'a_pandas_ex_horizontal_explode', 'a_pandas_ex_lookupdict', 'a_pandas_ex_multiloc', 'a_pandas_ex_obj_into_cell', 'a_pandas_ex_plode_tool', 'a_pandas_ex_to_tuple', 'ansi', 'flatten_everything', 'flexible_partial', 'numexpr', 'numpy', 'opencv_python', 'pandas', 'scikit_learn'],
    include_package_data=True
)
#python setup.py sdist bdist_wheel
#twine upload dist/*