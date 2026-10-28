from setuptools import setup, find_packages

setup(
    name="viddl",
    version="0.1.0",
    description="Кроссплатформенный загрузчик видео (YouTube, TikTok, Instagram, ...)",
    packages=find_packages(exclude=("tests",)),
    python_requires=">=3.10",
    install_requires=[
        "yt-dlp>=2024.4.9",
        "instaloader>=5.10.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "tqdm>=4.66.0",
        "PyYAML>=6.0",
        "click>=8.1.0",
    ],
    entry_points={"console_scripts": ["viddl=viddl.cli:main"]},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Environment :: Console",
        "Topic :: Multimedia :: Video",
    ],
)