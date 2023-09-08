from setuptools import setup, find_packages

setup(
    name="fmp-x",
    version="0.1.4",
    description="fmp quant client",
    author="Ron Stark",
    packages=find_packages(),
    install_requires=[
        "numpy==1.25.2",
        "pandas==2.1.0",
        "python-dotenv==1.0.0",
        "python_dateutil==2.8.2",
        "Requests==2.31.0",
        "retry==0.9.2",
    ],
    entry_points={
        "console_scripts": [
            # 如果你的包包含可执行脚本，这里列出它们
        ],
    },
)
