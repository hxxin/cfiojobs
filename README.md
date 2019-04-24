A script bundle that helps you to run fio benchmark on a cluster, and generate an excel fio test report for your. Makes your disk testing much easier.

This script is a fio jobs and file distributor. You can also run commands on multiple hosts with it.
Remenber, you need passwordless SSH access permssions for all hosts, and use a comma as a delimiter when you have multiple group units.

usage :
--------
1. Edit your own host group, block group and fio job type settings in config files.

            (1)     hosts  list conf:   ./cfiojobs.grp
            (2)     blocks list conf:   ./cfiojobs.blk
            (3)     jobs   list conf:   ./cfiojobs.job

    tips: 

            './cfiojobs -e' will generate example configure files for you

2. Run a short single cmd: 

            ./cfiojobs <options> [commands]

            options: 
            -t             check host group config file format (experimental).
            -g groups      run commands on given host groups which were defined in ./cfiojobs.grp (sep with comma)
                           (note that all the host group info will be reloaded when signal 1 is recived.)
            -L             list all available host group names in ./cfiojobs.grp.
            -a             run commands on all host groups set
            -x hosts       exclude hosts form hosts list (sep with comma)
            -X groups      exclude host groups form host groups list (sep with comma)
            -q             return only exit status of command.(be quiet and less output if no error occurred)
            -d             check and show most function parameters, also, skip failure
            -f             skip failure and try to continue, if possible
            -p             make send commands and copy files action executed in parallel
            --cpid         copy ssh pub id to given host groups 
            --script       execute given scripts on host groups (files sep with comma) 
            --argument     pass given arguments(double quote multiple args) to each given script  
            -w             run commmand on given hosts (sep with comma)
            -U             specify ssh user for hosts '-w' specified
            -P             specify ssh port for hosts '-w' specified
            --strictly     execute with a more precise scale control of concurrency (True|False)
            --conflict-ok  cancle pre conflict check befoe launch a test(don't use it if not nessary!).
            --no-ping      no ping check for hosts.
            --sudo         use sudo as a prefix for all command 

    Example: 
   
            ./cfiojobs -q -g grp1,grp2,grp3,grp4 "systemctl status sshd ;ls abc" -x 172.18.211.105
            ./cfiojobs -q -g grp1,grp2,grp3,grp4 --script ./tmp/install.sh --argument "-stable" -x 172.18.211.105

    tips:
    say you want run the command:
    
            'ls -i' 

    you can use: 

            ./cfiojobs ls -i -g vmg1,grp3 -t -d
      
    it is fine, because '-i' does not conflict with any options supported by this script,
    but still we strongly recommend you write it this way:

            ./cfiojobs "ls -i" -g vmg1,grp3 -t -d

    if you have scripts with different argument to pass in, you'd better execute them separately.

3. Example of Some more complex situation. (how to use double/single quote to pass the complete cmd to script):

        (1).with multy command a time:  
            ./cfiojobs  -g <grp name> "command1 ;  command2 ;  command3 "

         with command list to run :  
            ./cfiojobs  -g <grp name> "command1 && command2 || command3 "

        (2).with pipe thing or some  :  
            ./cfiojobs  -g <grp name> "your command |pipe |pipe "

        (3).with local bash variable :  
            ./cfiojobs  -g <grp name> "your command $local_variable "
            
        (4).with remote env variable :  
            ./cfiojobs  -g <grp name> "your command '$remote_env_viriable' " 

    example: 
            
            ./cfiojobs -g grp1 "ls -l |awk '{print\$2}'"
         
    or: 

            ./cfiojobs -g grp1 "ls -l |awk \"{print\\\$2}\""
       
    tips: 

            awk variable is different from bash shell variable, so there were three antislash inside curly braces,
            first two antislash passed an '\' to remote bash, and then the third is for translating the '$' inside awk.

4. FIO jobs control
    
            options:
            --fio          launch a fio test
            --fio-list     output a summary list of a given host group
            --fio-stop     stop all existinging fio jobs on given host groups (stop running jobs of a certain round)
            --test-stop    stop test on given host groups (stop all test and all running fio jobs on this group)
            --recover      recover unfinished test from where it was interrupted (aborted, killed or cancled)
            --recover-from recover or restart a test from given "round number" (and "blk group name") of it
            --round-list   list all job round based on the test options and arguments that are given (without launch a test)
            --round-retest retest only one round of jobs batch with a given "blk group name" and "round number"
                           round range like: "6-9" or: "blk8,6-9" are both ok, if you need the blk group name specified.
            -c             check test env, (network, ssh connections, fio installation, blk dev to test)
            -o             set the output dir for all fio test logs.
            -r             run test on ceph rbd blk.
            -b             run fio jobs with given blk group in ./cfiojobs.blk
            -j             run fio job with given job group in ./cfiojobs.job
            -s             single block mode, one block a time on each host.
            -S             single group mode, test one group after another till the end.
            -A             fio task 'After' commands that are given
            -E             run the commands everythime fio test batch starts on a host 
            -l             list all running fio test info.

    example: 

            ./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1 -o test01 
            ./cfiojobs --fio-list -g group1 -p
        
    you can have the current round info from script stdout or log file:
    
            "<output_dir>/recover.log", 
    you can easyly recover the test with with a certin round point in test progress, say, to recover the previous test with blk 
    target "blk8" and round "6", you can use the command :         

            ./cfiojobs --fio -g grp1 -b vd5,file8 -j rand1 --recover-from blk8,6 -o test01 
        
    or recover a test with only one blk group:
    
            ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover-from 6 -f -o test02 
    
    or recover the test from where you don't know:
    
            ./cfiojobs --fio -g grp1 -b vd5 -j rand1,mix1 --recover -f -o test02 
    
    note:
        
            when both the commands and fio jobs were running on a given host, they will be execute in parallel,
            but fio jobs will be send first by default, you can use '-A' to let command execute first.
            ./cfiojobs --fio -g grp1 -b vd5,blk8 -j rand1,mix1 -A "umount /dev/vdb" -o grp1_parallel_test01

    tips:

    **remanber to check the test env befor you start your fio test on a group:**
    
            ./cfiojobs -g <group name> -f -c

5. File distribution

            options:
            -D files       distribute files(sep with comma) to remote host
            -C files       collect files(sep with comma) from remote to local host
            -T dir         target/destination directory on remote host (home directory by default)

    example: 
    
            ./cfiojobs -g grp1 -F file1,file2,file3 -D /tmp/180730/ -x 172.18.211.137

6. Help info

            options:
            -h, --help     show this help info
            -e             make examples of config file (when they do not exist)
            -v, --version  show version info

    If an option requires an argument to work, you are not allowed to combine it with other options,
    you can use :

            ./cfiojobs -g <group name> -f -c 
            or 
            ./cfiojobs -g <group name> -fc 

    but the option -g requires an argument of host group name, for this case, you cannot put ~~' -gfc '~~ together!

