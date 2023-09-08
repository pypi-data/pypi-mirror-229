def install_polyglot_func():
    import shutil
    import sys
    import os
    import subprocess
    import tempfile

    def download_polyglot_dependencies():
        import os
        import sys
        from packaging import version
        from git import Repo

        # Directory path where the wheel files are located
        directory_path = "./polyglot_dependency_repo"

        # Download and install PyICU and pycld2 from your GitHub repo
        if not os.path.exists(directory_path):
            Repo.clone_from('https://github.com/thyripian/polyglot.git', directory_path)


        # Initialize an empty dictionary to store package versions
        package_versions = {}

        # Determine the Python version in the cpXXX format
        python_version = f"cp{sys.version_info.major}{sys.version_info.minor}"

        # Iterate through subdirectories
        for subdirectory in os.listdir(directory_path):

            subdirectory_path = os.path.join(directory_path, subdirectory)

            # Check if the subdirectory is a directory
            if os.path.isdir(subdirectory_path):

                all_files = os.listdir(subdirectory_path)

                # Filter for wheel filenames
                wheel_filenames = [filename for filename in all_files if filename.endswith(".whl")]

                # Proceed only if there are wheel filenames in this subdirectory
                if wheel_filenames:

                    # Create a dictionary to store versions based on Python version
                    versions_by_python = {}

                    # Extract versions and Python versions from wheel filenames
                    for filename in wheel_filenames:
                        parts = filename.split("-")
                        package_version = parts[1]
                        wheel_python_version = parts[2]
                        versions_by_python.setdefault(wheel_python_version, []).append(package_version)

                    # Determine the highest version for each Python version
                    highest_versions = {wheel_python_version: max(versions, key=version.parse) for wheel_python_version, versions in versions_by_python.items()}

                    # Store the highest versions in the dictionary
                    package_versions[subdirectory] = highest_versions
        packages = {}
        # Get the highest version for the current Python version
        for k,v in package_versions.items():
            if python_version in v.keys():
                highest_version = v[python_version]
                package_path = os.path.join(directory_path, k, f"{k}-{highest_version}-{python_version}-{python_version}-win_amd64.whl")
                print(f"Package: {k}, Highest Version for {python_version}: {highest_version}, File Path: {package_path}")
                packages[k] = package_path
                
        return packages

    def remove_directory(directory_path):
        # Remove all files
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                remove_directory(file_path)
        # Remove the directory itself
        os.rmdir(directory_path)

    print('Attempting to install polyglot.')

    # Check if git.Repo is already installed
    try:
        from git import Repo
    except ModuleNotFoundError:
        subprocess.run(['pip', 'install', 'GitPython'], check=True)
        from git import Repo
    # Check if polyglot is already installed
    try:
        import polyglot
        from polyglot.text import Text, Word
        print('Polyglot is installed and importable!')
        
    except ModuleNotFoundError:

         # Check and remove existing Polyglot folders in Python path
        for path in sys.path:
            polyglot_path = os.path.join(path, 'polyglot')
            if os.path.exists(polyglot_path):
                remove_directory(polyglot_path)

        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone polyglot repository into the temporary directory
            Repo.clone_from('https://github.com/aboSamoor/polyglot.git', temp_dir)
            
        # Move polyglot to Python's site-packages
        site_packages_path = os.path.join(sys.prefix, 'Lib', 'site-packages')
        if not os.path.exists(os.path.join(site_packages_path,'polyglot')):
            try:
                shutil.move('./polyglot_repo/polyglot', site_packages_path)
            except shutil.Error as e:
                remove_directory(os.path.join(site_packages_path,'polyglot'))
                shutil.move('./polyglot_repo/polyglot', site_packages_path)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")            
        
        packages = download_polyglot_dependencies()
        
        for k,v in packages.items():
            # remove existing package directories, if they exist
            if os.path.exists(os.path.join(site_packages_path,v)):
                remove_directory(os.path.join(site_packages_path,v))
            # Install the dependencies
            subprocess.run(['pip', 'install', v], check=True)

        
        # Check if morfessor is already installed
        try:
            import morfessor
        except ImportError:
            # remove existing package directories, if they exist
            if os.path.exists(os.path.join(site_packages_path,'morfessor')):
                remove_directory(os.path.join(site_packages_path,'morfessor'))
            # Install morfessor
            subprocess.run(['pip', 'install', 'morfessor'], check=True)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        
        # Test import
        try:
            import polyglot
            from polyglot.text import Text, Word
            print("Successfully installed polyglot and its dependencies.")
        except ImportError:
            print("Failed to install polyglot and its dependencies.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
