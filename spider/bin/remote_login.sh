#!/usr/bin/expect -f

set ip [ lindex $argv 0 ]
set password [ lindex $argv 1 ]
set timeout 10
set cmd "cd /root/work/sda; git status; sleep 3;"

spawn ssh root@$ip
expect {
"*yes/no" { send "yes\r"; exp_continue}
"*password:" { send "$password\r" }
}


#interact

expect "#*"
send "$cmd\r"
send  "exit\r"
expect eof