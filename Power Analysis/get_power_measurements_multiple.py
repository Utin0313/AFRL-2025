#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  get_power_measurements_multiple.py
#  
#  Copyright 2025  <ucanlab@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

#!/usr/bin/env python3
# Multi-ZMQ power reader (float32 frames) — prints CSV per iteration
import sys, getopt, time, zmq, numpy as np

def zmq_measure(sock):
    latest = None
    try:
        while sock.poll(0):
            latest = sock.recv(flags=zmq.NOBLOCK)
    except zmq.Again:
        pass
    if latest is None:
        return 0.0
    arr = np.frombuffer(latest, dtype=np.float32, count=-1)
    return float(np.average(arr)) if arr.size else 0.0

def main(argv):
    node = "182"
    reps = 1
    delay = 1.0
    ports = [55555, 55556, 55557]
    try:
        opts, _ = getopt.getopt(argv, "hn:r:t:p:")
    except getopt.GetoptError:
        print('get_power_multi.py -n <node> -r <reps> -t <delay_s> [-p 55555,55556,55557]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print('get_power_multi.py -n <node> -r <reps> -t <delay_s> [-p 55555,55556,55557]')
            return
        elif opt == "-n":
            node = arg
        elif opt == "-r":
            reps = int(arg)
        elif opt == "-t":
            delay = float(arg)
        elif opt == "-p":
            ports = [int(x) for x in arg.split(",") if x.strip()]

    ctx = zmq.Context.instance()
    subs = []
    for prt in ports:
        s = ctx.socket(zmq.SUB)
        s.setsockopt(zmq.SUBSCRIBE, b"")
        s.connect(f"tcp://10.1.1.{node}:{prt}")
        subs.append(s)

    time.sleep(2)  # allow connects
    # optional header:
    # print(",".join(str(p) for p in ports))

    for _ in range(reps):
        vals = [zmq_measure(s) for s in subs]
        print(",".join(f"{v:.6g}" for v in vals))
        time.sleep(delay)

if __name__ == "__main__":
    main(sys.argv[1:])
