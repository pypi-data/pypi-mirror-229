import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

setuptools.setup(
    name="deepface-customized",
    version="0.0.1",
    author="Huzaifa Tariq",
    author_email="huzaifat65@outlook.com",
    description="Modified DeepFace library for specific custom use",
    long_description="""Deepface is a lightweight face recognition and facial attribute analysis (age, gender, emotion and race) framework for python. It is a hybrid face recognition framework wrapping state-of-the-art models: VGG-Face, Google FaceNet, OpenFace, Facebook DeepFace, DeepID, ArcFace, Dlib and SFace.
                        \nExperiments show that human beings have 97.53% accuracy on facial recognition tasks whereas those models already reached and passed that accuracy level.
                        \nThe source code of this library has been modified for the custom use only
                    """,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["deepface = deepface.DeepFace:cli"],
    },
    python_requires="==3.8.4",
    install_requires=requirements,
)
