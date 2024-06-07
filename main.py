import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


# Create dictionary to store variables necessary to generate the config
def get_config_items(lines):
    config_items = {}

    # Add timestamp to dictionary
    config_items["time_now"] = get_time()

    # Define the regex pattern for MAC addresses
    mac_pattern = r"(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"
    mac_count = 0

    # Scrape all mac addresses, count them, and extract device hostname from the show command
    config_items["mac_addresses"] = []
    for line in lines:
        if "#" in line:
            # Split the line at '#' and strip any whitespace from the part before '#'
            hostname = line.split("#")[0].strip()
            config_items["hostname"] = hostname

        # Search for mac address, if match store value in dictionary
        match = re.search(mac_pattern, line)
        if match:
            config_items["mac_addresses"].append({"mac": match.group()})
            mac_count += 1

    # Add the count of mac addresses into the dictionary
    config_items["mac_count"] = mac_count

    return config_items


# Get the current local date/time and format the object to a string in a readable format
def get_time():
    time = datetime.now()
    time = time.strftime("%Y-%m-%d_%Hh%Mm")
    return time


if __name__ == "__main__":
    # Define variables
    file_path = "show_eapol_session_output.log"
    file_content = None

    # Open the txt file with the output from the 'show eapol sessions' command
    with open(file_path, "r") as file:
        file_content = file.read()

    # Split the string into lines
    lines = file_content.splitlines()

    # Create python dictionary with all variables for generating the config
    config_items = get_config_items(lines)

    # Create jinja environment and load the template file
    env = Environment(
        loader=FileSystemLoader("."), trim_blocks=True, lstrip_blocks=True
    )
    template = env.get_template("config_template.j2")

    # Generate config by rendering the dictionary
    switch_config = template.render(config_items)

    hostname = config_items.get("hostname")
    mac_count = config_items.get("mac_count")

    # Create txt file with hostname switch as name and save all config
    with open(f"{hostname}+_port_sec_config.txt", "w", encoding="utf-8") as w:
        w.write(switch_config)
        w.write("\n\n")
        w.write("*" * 70)
        w.write(
            "\nBelow is the original output from the show eapol session command for reference."
        )
        w.write(
            "\nCheck if total authenticated mac is the same as mac addresses in generated config.\n"
        )
        w.write("*" * 70)
        w.write("\n")
        w.write(file_content)

        # Show progress in terminal
        print()
        print("*" * 60)
        print(f"Port security config for switch {hostname} has been generated.")
        print(f"There are {mac_count} MAC addresses added in the security list config.")
        print("*" * 60)
