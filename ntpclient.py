from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime

NTP_PACKET_FORMAT = ">12I" # unpacking 12 unsigned intergers (32 bits) 
NTP_DELTA = 2208988800  # 1970-01-01 00:00:00

def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float,
float):
       cpkt = bytearray(48)
       cpkt[0] = 0x1B #
       T1 = datetime.now().timestamp()
       #print(T1)  
       with socket(AF_INET, SOCK_DGRAM) as s:
           s.sendto(cpkt, (server, port))
           pkt,_=s.recvfrom(48)
           T4 = datetime.now().timestamp()       
           return (pkt, T1, T4)
       
      

def ntpPktToRTTandOffset(pkt, T1, T4) -> (float, float):
    # Unpack the NTP packet to extract the two timestamps (T2 and T3)
    unpacked = struct.unpack(NTP_PACKET_FORMAT, pkt[0:48])
    T2_seconds = unpacked[8] -NTP_DELTA
    T2_fraction = float(unpacked[9]) / 0x100000000
    T3_seconds = unpacked[10]-NTP_DELTA
    T3_fraction = float(unpacked[11]) / 0x100000000

    # Combine the seconds and fractions into floating-point numbers
    T2 = T2_seconds + T2_fraction
    T3 = T3_seconds + T3_fraction

    # Compute the RTT and offset
    RTT = (T4 - T1) - (T3 - T2)
    offset = ((T2 - T1) + (T3 - T4)) / 2.0
    #print(offset)

    return RTT, offset


def getCurrentTime(server="time.apple.com", port=123, iters=20) -> (float):
    offsets = []
    for _ in range(iters):
        p, T1, T4 =  getNTPTimeValue(server, port)
        rtt, offset = ntpPktToRTTandOffset(p, T1, T4)
    offsets.append(offset)
    
    if offsets:
        # Return the median offset as the current time
        avg_offset = sum(offsets) / len(offsets)
        current_time = datetime.now().timestamp() + avg_offset
        return current_time
    else:
        return None

if __name__ == "__main__":
    print(getCurrentTime())