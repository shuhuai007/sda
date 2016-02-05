#!/usr/bin/expect -f

set ip [ lindex $argv 0 ]
set password [ lindex $argv 1 ]
set timeout 100
set cmd1 "cd /root/work/sda/spider/bin; git status; sleep 3;"
set cmd2 [ lindex $argv 2 ]

spawn ssh root@$ip
expect {
"*yes/no" { send "yes\r"; exp_continue}
"*password:" { send "$password\r" }
}


#interact

expect "#*"
send "$cmd1\r"
send "$cmd2\r"
send  "exit\r"
expect eof