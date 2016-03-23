### Usage: fetch topic, question, answer, user info from https://www.zhihu.com
####./slave-control.sh  -i \<ip>  -p \<password> -c \<content> start/status


For example:   
##### 1. start to generate zhihu topic data 
` `\# cd /sda/spider/bin  
` `\# ./slave-control.sh -i 127.0.0.1 -p ${password} -c topic start


##### 2. start to generate zhihu question data 
` `\# cd /sda/spider/bin  
` `\# ./slave-control.sh -i 127.0.0.1 -p ${password} -c question start

##### 3. start to generate zhihu answer data 
` `\# cd /sda/spider/bin  
` `./slave-control.sh -i 127.0.0.1 -p ${password} -c answer start

##### 4. Generate zhihu user info
` `\# cd sda/spider/entity  
` `\# nohup python zhihu_user.py > user.log 2>&1 &
