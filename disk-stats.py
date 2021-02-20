import sys
import psutil
import re
from time import sleep
from os import system

#Matches disks that are sd then any letter. Doesn't match partitions
sda_regex = re.compile("^sd[A-Za-z]$")
#Matches disks that start with nvme then any letter, the letter n then a number. Doesn't match partitions.
nvme_regex = re.compile("^nvme[\\d]{1}n[\\d]{1}$")


#Select whether you want info on disks or partitions
mode = "disk"

def clear_screen():
    system('clear')

def refresh_disk_stats(all=False):
    #Dict containing the data about the disks we are interested in
    disk_data = {}
    #Data for all disks and all partitions
    blob = psutil.disk_io_counters(perdisk=True)
    if all:
        for k,v in blob.items():
            #Filter out things that are not disks or partitions
            if "loop" not in k and "dm-" not in k and "zram" not in k:
                disk_data[k] = {"bytes_read" : v.read_bytes, "bytes_written": v.write_bytes}
    else:
        #Loop through blob and pull out the data we are interested
        for k,v in blob.items():
            if sda_regex.match(k) or nvme_regex.match(k):
                disk_data[k] = {"bytes_read" : v.read_bytes, "bytes_written": v.write_bytes}

    
    return disk_data

#Convert bytes to human readable numbers
def output_most_readable_number(bytes):
    #If it's less than a KB then return bytes
    if bytes < 1024:
        return f"{bytes} B/s"
    #If it's greater than a KB and less than an MB return KBs
    if bytes > 1024 and bytes < 1024**2:
        return f"{bytes / 1024} KB/s"
    #If it's greater than a MB and less than an GB return MBs
    if bytes > 1024 * 1024 and bytes < 1024**3:
        return f"{bytes / 1024**2} MB/s"
    if bytes > 1024**3:
        return f"{bytes / 1024**3} GB/s"
     


def print_rw_per_sec():
    running = True
    try:
        while running:
            #Container for computed rw per sec
            rw_data = {}
            #Get initial rw info for disks
            initial_data = refresh_disk_stats()
            #Wait 1 second and then grab the rw data again
            sleep(1)
            clear_screen()
            fresh_data = refresh_disk_stats()
            print("Disk IO Information\n")
            print("Press CTRL + C to quit\n")


            #Loop through the fresh_data: for each disk in fresh_data and minus the initial value from the fresh value.
            #Add the computed rw data to rw_data
            for k,v in fresh_data.items():
                read_ps = fresh_data[k]["bytes_read"] - initial_data[k]["bytes_read"]
                write_ps = fresh_data[k]["bytes_written"] - initial_data[k]["bytes_written"]
                rw_data[k] = {
                    "read_per_second" : output_most_readable_number(read_ps),
                    "write_per_second" : output_most_readable_number(write_ps)
                    }
            
            #Print the information
            for k,v in rw_data.items():
                print(k)
                print(f"Read: {v['read_per_second']}")
                print(f"Write: {v['write_per_second']}")
                print("\n")

    except KeyboardInterrupt:
        print("\nQuitting\n")
        sys.exit()


def main():
    print_rw_per_sec()

if __name__ == "__main__":
    main()        