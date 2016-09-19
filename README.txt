               ------------------------------------------------
               Tunneling UDP Packets through SSH to Secure VoIP
               ------------------------------------------------
                                   README
                                   
********************************************************************************
Contents:
    ./src       source code
    ./img       screenshots
    ./doc       documents and reports
    
********************************************************************************
Introduction:
The system implements a secure means of transmitting UDP data in VoIP by using a
hybrid TCP/UDP tunnel that uses the best features of existing tunneling and VPN 
protocols along with an encryption mechanism similar to that of SSH to secure 
traffic between two terminals transmitting voice and text.

The system is made in Python 2.7 and uses WxPython for the Graphical User 
Interface and has been extensively tested to provide the best possible 
experience.

********************************************************************************
Installation:
    - A POSIX compliant system (Linux, Mac OS X) is required.
    - A working Python 2.7 installation is required.
    - Following additional Python libraries are to be installed:
        > PyCrypto
        > PyAudio
        > WxPython
        > dict
        
********************************************************************************
Usage:
    - The system can be run by executing run.py
        $ python run.py [options]...
    - run.py takes following parameters:
        -c        run as client
        -h        display help
    - When no parameters are specified, the system runs as server.

********************************************************************************
Configuration:
    - All configuration options are stored in the file config.txt which can 
      either be edited by hand or from the GUI Settings tab.

********************************************************************************
Authors:
    - Sameer Jain
    - Saeesh Kakodkar
    - Viren Nadkarni (@viren-nadkarni)
    - Pranav Prem (@vanarp96)
