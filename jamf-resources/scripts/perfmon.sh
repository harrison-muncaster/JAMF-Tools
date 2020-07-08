#!/usr/bin/env bash

  # Standard boilerplate

unset ${scriptName} ${me} ${now}
scriptName="$(basename "$(test -L "$0" && readlink "$0" || echo "$0")")"
now="$(date +%y%m%d_%H%M%S)"
logfileName="$(date +%F\[%a\].performance.csv)"
operationUseage=$(cat <<EOF

Invalid operation. --operation must be set to one of the following functions:

    --operation  log            Logs performance data

    --operation  tar            Archives previously created log entries


EOF
)


  # Define a simple function to perform the cleanup function predicably

tar-get() {
  local directory output
  deleteFiles=0
  DebugOutput=0

  while [[ ${1} ]]; do
    case "${1}" in
    --directory)
      directory=${2}
      shift
      ;;
    --suffix)
      suffix=${2}
      shift
      ;;
    --output)
      output=${2}
      shift
      ;;
    --delete)
      deleteFiles=1
      ;;
    --debug)
      DebugOutput=1
      ;;
    *)
      echo "Unknown parameter: ${1}" >&2
      return 1
      ;;
    esac

    if ! shift; then
      echo 'Missing parameter argument.' >&2
      return 1
    fi
  done

  if [[ -z ${directory} || -z ${suffix} ]]; then
    echo "${FUNCNAME}: one or more variables are undefined"
    return 1
  fi
  datestamp="$(date +%s)"

  cd ${directory}
  prefix=$(echo "$(pwd | tr "/" "-")")
  archive_name=$(echo "${prefix#-}:${datestamp}.${suffix}.tar.gz")
  cd -
  tar -czf ${archive_name} ${directory}/*.${suffix} &>/dev/null


  if [[ ! -z ${output} ]]; then
    mv ./${archive_name} ${output}
  fi

  if [[ deleteFiles -eq 1 ]]; then
    rm -f ${directory}/*.${suffix}
    fi

}

  # Parse input validation

while [[ ${1} ]]; do
    case "${1}" in
      --operation)
        operation=${2}
        shift
        ;;
      --debug)
        debugOutput=1
        ;;
        *)
          echo "Unknown parameter: ${1}" >&2
          exit 1
          ;;
        esac

        if ! shift; then
          echo 'Missing parameter argument.' >&2
          exit 1
        fi
      done

  # Ensure that required params have been set

      if [[ -z ${operation} ]] \
        ; then
        echo "${scriptName}: one or more required params are undefined"
        exit 1
      fi

  # Give us a hint if we get jammed up

      [[ debugOutput -gt 0 ]] && echo "operation set to: ${operation}"

  # Pefrom input validation on the operation switch; eject and print help info if it doesn't match one of our known operations

case ${operation} in
    log | tar)
    ;;
    *)
    echo "${operationUseage}"
    exit 1
    ;;
 esac

 # Execute program flow now that we've verified our inputs

 case ${operation} in
    log )

          # Configure values for the variables required for the operation

          header="time,#physical-cores,#logical-cores,%cpu-system,%memory-system,process-rank,process-name,%cpu-process,%mem-process"

          physicalCores="$(sysctl -n hw.physicalcpu)"
          logicalCores="$(sysctl -n hw.logicalcpu)"
          cpuUtilization="$(ps -A -o %cpu | awk '{s+=$1} END {print s "%"}')"
          memoryUtilization="$(echo 100-$(memory_pressure | tail -n 1 | awk '{print $NF}' | tr -d '%') | bc)%"
          topProcs="$(ps aux | sort -nrk 3,3 | head -n 10 | awk '{print $11 " "  $3 "% " $4 "%"}' | tr " " ",")"


          # Set extra loop variales, the feed top processes into the loop, iterating to stringbuild each line in the csv

          csvOutput=""
          counter=1
            while read line; do
              csvOutput+="${now},${physicalCores},${logicalCores},${cpuUtilization},${memoryUtilization},${counter},${line}\n"
              ((counter++))
              done < <( echo "${topProcs}")

          # Add the header only if the file does not already exist

          [ -r ~/"${logfileName}" ] ||
            echo "${header}" > ~/"${logfileName}"

          # Append the final csv data into the logfileName

            echo -en "${csvOutput//$'\n'/}" >> ~/"${logfileName}"
          ;;
    tar )

      # Perform simple cleanup

          tar-get --directory "$(pwd)/" --suffix performance.csv --delete
          ;;
     *)
         echo "${operationUseage}"
         exit 1
         ;;
  esac



exit 0
