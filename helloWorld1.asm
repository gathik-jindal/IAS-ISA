NOP ; STOR M(20)
STOR M(21) ; ADD M(51)
STOR M(22) ; JUMP- M(107,20:39)
LOAD M(20) ; INR M(21)
ADD M(21) ; STOR M(20)
INR M(22) ; LOAD M(22)
JUMP M(3,20:39) ; LOAD M(20)
DIV M(22) ; LOAD MQ
STOR M(22) ; END

0
1
0
0
0
0
0
0
0
0