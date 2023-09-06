from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="my_img_2_txt",
    version="0.0.1",
    author="Michelle Santos",
    author_email="michellesantosvet@gmail.com",
    description="Transform images with texts on it into a single text",
    long_description="Transforms images into text using cv2 and pytesseract libraries",
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=['opencv', 'pytesseract'],
    python_requires='>=3.8',
)