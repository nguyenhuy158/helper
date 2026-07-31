#!/usr/bin/env python3
"""
Test script for the helper library interface.
This script demonstrates how to use helper functions programmatically.
"""

import os
import sys

# Add src/ to path for development testing (run from repo without install)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import helper


def test_disk():
    """Test disk functions."""
    print("=== Testing Disk Functions ===")

    try:
        usage = helper.disk.get_usage()
        print("Disk usage:")
        print(usage)
        print()

        mount = helper.disk.get_mount()
        print("Disk mount:")
        print(mount)
        print()

        list_info = helper.disk.get_list()
        print("Disk list:")
        print(list_info)
        print()

    except Exception as e:
        print(f"Error testing disk functions: {e}")
        print()


def test_system_info():
    """Test system info function."""
    print("=== Testing System Info ===")

    try:
        info = helper.system_info.get_info()
        if info:
            print("System:", info["system"]["system"], info["system"]["release"])
            print("Node:", info["system"]["node"])
            print("Machine:", info["system"]["machine"])
            print("Processor:", info["system"]["processor"])
            print("OS Version:", info["os_version"])
            print("Uptime:", info["uptime"])
            print("CPU Cores:", info["cpu"]["cores"])
            if "cpu" in info["cpu"]:
                print("CPU:", info["cpu"]["cpu"])
            if "load_avg" in info["cpu"]:
                print("Load Average:", info["cpu"]["load_avg"])
            print("Memory:", info["memory"])
            print(
                "Disks:", info["disks"][:100] + "..." if len(info["disks"]) > 100 else info["disks"]
            )
        else:
            print("System info not available")
        print()

    except Exception as e:
        print(f"Error testing system info: {e}")
        print()


def test_network():
    """Test network functions."""
    print("=== Testing Network Functions ===")

    try:
        ip = helper.internal_ip.get_internal_ip()
        print("Internal IP:", ip)

        pub_ip = helper.public_ip.get_public_ip()
        print("Public IP:", pub_ip)

        arch = helper.arch.get_arch()
        print("Architecture:", arch)
        print()

    except Exception as e:
        print(f"Error testing network functions: {e}")
        print()


def test_all_info():
    """Test all info function."""
    print("=== Testing All Info ===")

    try:
        all_info = helper.all_info.get_info()
        print("Internal IP:", all_info["internal_ip"])
        print("Public IP:", all_info["public_ip"])
        print("Architecture:", all_info["arch"])
        print("System Info available:", "system_info" in all_info)
        print()

    except Exception as e:
        print(f"Error testing all info: {e}")
        print()


def test_speed():
    """Test speed function (may take time)."""
    print("=== Testing Speed (commented out to avoid long test) ===")
    # Uncomment to test speed (takes ~30 seconds)
    # try:
    #     result = helper.speed.get_speed()
    #     if 'error' in result:
    #         print("Speed test error:", result['error'])
    #     else:
    #         print("Ping:", result['ping'], "ms")
    #         print("Download:", helper.speed.format_speed(result['download']))
    #         print("Upload:", helper.speed.format_speed(result['upload']))
    # except Exception as e:
    #     print(f"Error testing speed: {e}")
    print("Speed test skipped (uncomment in code to run)")
    print()


def main():
    """Run all tests."""
    print("Testing Helper Library Interface")
    print("=" * 40)

    test_disk()
    test_system_info()
    test_network()
    test_all_info()
    test_speed()

    print("Library interface test completed!")


if __name__ == "__main__":
    main()
