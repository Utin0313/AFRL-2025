#!/bin/bash

#################################################################### 
# sdr_get_data.sh
#
# Author: MR
#
# Description: This script gets power measurements from specified 
#    nodes over a range of frequencies.
#
# Input: 
#
# **For Help, enter -h**
#
####################################################################
#############################
#####     Functions     #####
#############################
#---------------------------------------------------------------------------------------------

help()
{
	echo ""
	echo "	### Bash script to get power measurements at specified nodes ###"
	echo "	---------------------------------------------------------------------------------------"
	echo "	-l = list of client node addresses (e.g., 'bash sdr_get_data.sh -l 103,105,109')"
	echo "	-r = range of client node addresses (e.g., 'bash sdr_get_data.sh -r 103,107')"
	echo "	-c = desired carrier frequencies (OPTIONAL) (e.g., 'bash sdr_get_data.sh -c 912000000,915000000')"
	echo "	-i = number of iterations (e.g., 'bash sdr_get_data.sh -i 10')"
	echo "	-u [OPTIONAL] = input client's username if the default one (ucanlab) is not used"
	echo ""
	exit
}

#---------------------------------------------------------------------------------------------
# Creates array from command line inputs
addresses_list()
{
	IFS=','
	read -ra my_addresses <<< "$OPTARG"
}

#---------------------------------------------------------------------------------------------
# Parse input and create ip array from arg1 through arg2
addresses_range()
{
	IFS=','
	read -ra temp <<< "$OPTARG"
	index=0
	for (( i=${temp[0]}; i<=${temp[1]}; i++ ))
	do
		my_addresses[$index]=$i
		index=$((index+1))
	done
}

#---------------------------------------------------------------------------------------------
# Creates array from command line inputs
carrier_freq_list()
{
	IFS=','
	read -ra my_carrier_freqs <<< "$OPTARG"
}

#---------------------------------------------------------------------------------------------
# Creates array from command line inputs
num_iterations_list()
{
	IFS=','
	read -ra my_num_iterations <<< "$OPTARG"
}

#############################
#####   Setup Params    #####
#############################
#---------------------------------------------------------------------------------------------
# Set default parameters

uname=ucanlab # default
debug=0

tx_xmlrpc_port=':8080'
rx_xmlrpc_port=':8081'
zmq_port=':55555'

#---------------------------------------------------------------------------------------------
# Get arguments and set appropriate parameters

while getopts 'hl:r:i:c:u:d' OPTION; do
	case "$OPTION" in
		h)
			help;;
		l)
			addresses_list;;
		r)
			addresses_range;;
		i)
			num_iterations_list;;
		c)
			carrier_freq_list;;
		u)
			uname=$OPTARG;; # in case the username is not the default one, use this flag to user another username
		d)
			debug=1;;
	esac
done

# Choose Iterations
num_iterations=0
if [[ ${#my_num_iterations[@]} -gt 0 ]]; then
    num_iterations="${my_num_iterations[0]}"
else 
    num_iterations=0
fi

# If -c was NOT provided, do one pass with "no carrier"
# (keeps the same loop structure, but prevents the loop from being empty)
use_carrier=0
if [[ ${#my_carrier_freqs[@]} -gt 0 ]]; then
    use_carrier=1
else
    my_carrier_freqs=("")
fi


#############################
#####     Main Code     #####
#############################
#-------------------------------------------------------------------

if [ $debug -gt 0 ]
then
	# for debugging... use -d flag
	echo ""
	echo "  ##### Debug Info: #####"
	echo "  Nodes: ${my_addresses[@]}"
	echo "  Carriers: ${my_carrier_freqs[@]}"
        echo "  Number of Iterations: ${my_num_iterations[@]}"
	echo "  UName: $uname"
	echo ""
	exit
fi	


#############################
#####     Main Code     #####
#############################
#------------------------------------------------------------------------------------


# Setup output headings

temp="   Node ID"

j=0
while [[ $j -lt ${#my_carrier_freqs[@]} ]]; do # loop through desired carriers
	my_fc=${my_carrier_freqs[$j]}

	if [[ $use_carrier -eq 1 ]]; then
		temp="$temp, fc=$my_fc "
	else
		temp="$temp"
	fi

	j=$((j + 1))
done

# Results Directoryhhh
results_dir="/home/ucanlab/ucan_TB/TB_Results/Prediction_Based_Measurements"
mkdir -p "$results_dir"


# Iterate through nodes
i=0
while [[ $i -lt ${#my_addresses[@]} ]]; do # loop through number of nodes
	# get desired values from list 
	my_addr=${my_addresses[$i]}
	temp="     $my_addr"

        # Per-node CSV (overwrite each run)
        csv_path="${results_dir}/Prediction_Values_${my_addr}.csv"
        echo "Iteration,Prediction" > "$csv_path"

        j=0
        while [[ $j -lt ${#my_carrier_freqs[@]} ]]; do # loop through desired carriers (or one dummy pass if none)
		  my_fc=${my_carrier_freqs[$j]}
		
		  # Set carrier ONLY if user provided -c
		  if [[ $use_carrier -eq 1 ]]; then
			  python3 SDR_control/set_remote_params_rx.py -n $my_addr -c $my_fc
			  rc=$?
			  if [[ $rc -ne 0 ]]; then
				  echo "WARNING: set_remote_params_rx.py failed (flowgraph may not support set_carrier_frequency). Continuing..."
			  fi
			  sleep 1
		  fi
                  
                  # Iterations (1..num_iterations)
                  iter=1
                  while [[ $iter -le $num_iterations ]]; do

                      measurement=$(python3 SDR_control/get_power_measurements.py -n "$my_addr" -r 1 -t 2)

                      printf "%s,%s\n" "$iter" "$measurement" >> "$csv_path"
                         
                      temp="Node $my_addr Prediction Capture into CSV Complete."
                         
                      iter=$((iter + 1))
                  done

                  j=$((j + 1))
        done

	i=$((i + 1))
        echo $temp
done

