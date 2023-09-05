
from iotellme import *
token='8eac160ca6a916e48eef5cc4b81e81bb0698e4d6c081862c3dbe8b877d398c8f'
users_id=1066
value=88
id1=1636
id2=1635
id3=1634
id4=1633
id5=1632
iotellme.Token(token,users_id)
iotellme.Write1(id1,value)
iotellme.Write2(id2,value)
iotellme.Write3(id3,value)
iotellme.Write4(id4,value)
iotellme.Write5(id5,value)
iotellme.Send()