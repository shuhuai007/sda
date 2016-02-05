#!/usr/bin/expect -f

set ip [ lindex $argv 0 ]
set password [ lindex $argv 1 ]
set timeout 100
set git_cmd "cd /root/work/sda/spider/bin; git reset --hard;git pull; sleep 3;"
set cmd [ lindex $argv 2 ]

spawn ssh root@$ip
expect {
"*yes/no" { send "yes\r"; exp_continue}
"*password:" { send "$password\r" }
}


#interact

expect "#*"
send "$git_cmd\r"
send "$cmd\r"
send  "exit\r"
expect eof