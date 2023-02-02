"""NXO Functions."""


def banner():
    """Display banner."""
    print(
        r"""
     ________  ________  ________  ___  ___  ________  ________  ________      
    |\   __  \|\_____  \|\   __  \|\  \|\  \|\   __  \|\   __  \|\   ____\     
    \ \  \|\  \|____|\ /\ \  \|\  \ \  \\\  \ \  \|\  \ \  \|\  \ \  \___|_    
     \ \   ____\    \|\  \ \   _  _\ \   __  \ \  \\\  \ \   ____\ \_____  \   
      \ \  \___|   __\_\  \ \  \\  \\ \  \ \  \ \  \\\  \ \  \___|\|____|\  \  
       \ \__\     |\_______\ \__\\ _\\ \__\ \__\ \_______\ \__\     ____\_\  \ 
        \|__|     \|_______|\|__|\|__|\|__|\|__|\|_______|\|__|    |\_________\
                                                                   \|_________|
    """
    )

def docs():
    """Help to understand the utility and directory meaning"""
    print(
        r"""
    results/:   Directory where snapshot are stored with the following naming convention {device}.{suffix}
    logs/:      Directory where logs from unicon (pyats library to connect to device) are stored
                with the following naming convention {device}.log
    
    testbed file is the prerequisite to use the tool and must be filled (check pyats documentation).
    Script only supports N9k/N3k fixed chassis.
    
    To compare 2 snapshots, use the diff tool under linux, example:
        Take a snapshot before an upgrade:
            user@linux-srv:~$ python3 nxos_parser.py -s before-upgrade
        
        Upgrade all your NXOS systems.... And take another snapshot after a successfull upgrade
            user@linux-srv:~$ python3 nxos_parser.py -s after-upgrade
        
        Compare the 2 snapshots, analyze quickly the output focusing on changes and make sure that the system is compliant !
            user@linux-srv:~$ diff results/nxos_switch.before-upgrade results/nxos_switch-1.after-upgrade

    """
    )
