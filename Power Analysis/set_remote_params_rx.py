#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from xmlrpc.client import ServerProxy
import sys, getopt
import time



def main(argv):

   node_id      = '101'
   fc           = ''
   rx_gain      = ''
   baseband_freq= ''
   bandwidth    = ''
   filter1_low  = ''
   filter1_high = ''
   filter2_low  = ''
   filter2_high = ''
   
   c_set = 0
   g_set = 0
   e_set = 0
   w_set = 0
   x_set = 0
   z_set = 0
   y_set = 0
   u_set = 0
   debug = 0
   
   try:
      opts, args = getopt.getopt(argv,"hn:c:g:x:z:y:u:d",["node_id=","fc=","rx_gain=","filter1_low=","filter1_high=","filter2_low=","filter2_high="])
   except getopt.GetoptError:
      print ('  test.py -n <node ID> -c <carrier frequency> -g <rx gain> -x <filter1 low> -z <filter1 high> -y <filter2 low> -u <filter2 high>')
      sys.exit(2)   
   for opt, arg in opts:
      if opt == '-h':
         print ('  test.py -n <node ID> -c <carrier frequency> -g <rx gain>')
         sys.exit()
      elif opt in ("-n", "--node_id"):
         node_id = arg
      elif opt in ("-c", "--carrier_freq"):
         fc = arg
         c_set = 1
      elif opt in ("-g", "--rx_gain"):
         rx_gain = arg
         g_set = 1
      elif opt in ("-x", "--filter1_low"):
         filter1_low = arg
         x_set = 1
      elif opt in ("-z", "--filter1_high"):
         filter1_high = arg
         z_set = 1
      elif opt in ("-y", "--filter2_low"):
         filter2_low = arg
         y_set = 1
      elif opt in ("-u", "--filter2_high"):
         filter2_high = arg
         u_set = 1
      elif opt in ("-d", "--debug"):
         debug = 1
         
   if debug == 1:
      print ('Node ID:           ', node_id)
      print ('Carrier Frequency: ', carrier_freq)
      print ('Rx Gain:           ', rx_gain)
   
   xmlrpc_control_client = ServerProxy('http://'+'10.1.1.'+node_id+':8081')


   if c_set == 1:
      xmlrpc_control_client.set_fc(int(fc))

   if g_set == 1:
      xmlrpc_control_client.set_rx_gain(int(rx_gain))

   if z_set == 1 and x_set == 1:
      xmlrpc_control_client.set_filter1_high(int(filter1_high))
      xmlrpc_control_client.set_filter1_low(int(filter1_low))
   else:
      if x_set == 1:
          xmlrpc_control_client.set_filter1_low(int(filter1_low))
      if z_set == 1:
          xmlrpc_control_client.set_filter1_high(int(filter1_high))
   
   if u_set == 1 and y_set == 1:
      xmlrpc_control_client.set_filter2_high(int(filter2_high))
      xmlrpc_control_client.set_filter2_low(int(filter2_low))
   else:
      if y_set == 1:
          xmlrpc_control_client.set_filter2_low(int(filter2_low))
      if u_set == 1:
          xmlrpc_control_client.set_filter2_high(int(filter2_high))  
   

if __name__ == "__main__":
   main(sys.argv[1:])
