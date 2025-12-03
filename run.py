import os
import sys
import platform
import subprocess

def run_docker(cmd_list):
    try:
        print(f"Executing: {' '.join(cmd_list)}")
        subprocess.run(cmd_list, check=True)
    except subprocess.CalledProcessError:
        print("Error executing command.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)

def main():
    os_name = platform.system()
    print(f"Detected OS: {os_name}")

    compose_files = ["docker-compose.yml"]

    docker_cmd = ["docker-compose"]

    if os_name == "Linux":
        print("Setting up for Linux...")

        try:
            subprocess.run(["xhost", "+local:docker"], check=False)
        except FileNotFoundError:
            print("Warning: 'xhost' command not found. GUI might not work.")

        compose_files.append("docker-compose.linux.yml")

        if os.geteuid() != 0:
            docker_cmd.insert(0, "-E")
            docker_cmd.insert(0, "sudo")

    elif os_name == "Windows" or os_name == "Darwin":
        print(f"Setting up for {os_name}...")
        print("NOTE: Ensure VcXsrv (Windows) or XQuartz (Mac) is running!")
        compose_files.append("docker-compose.windows.yml")
    else:
        print("Unsupported OS")
        sys.exit(1)

    separator = os.pathsep
    os.environ["COMPOSE_FILE"] = separator.join(compose_files)
    print(f"Loading configuration files: {os.environ['COMPOSE_FILE']}")

    docker_cmd.extend(["up", "--build"])

    run_docker(docker_cmd)

if __name__ == "__main__":
    main()