import setuptools

setuptools.setup(
    name = "Ananth2023DevOpsTeamList",
    version = "1.0.1",
    author="Ananth S S",
    description =  "Displays the DevOps Team List of Presidio",
    long_description = "Displays the DevOps Team List of Presidio",
    packages= setuptools.find_packages(),
    py_modules=["Ananth2023DevOpsTeamList"],
    package_dir={"": "Ananth2023DevOpsTeamList/src"},
    requires=["ascii_magic", "colorama", "requests"]
)