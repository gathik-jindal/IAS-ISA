LOAD M(X)
LOAD -M(X)
LOAD |M(X)|
LOAD -|M(X)|
ADD M(X)
SUB M(X)
ADD |M(X)|
SUB |M(X)| //fjasjflsad
LOAD MQ,M(X) ; LOAD MQ //fjasjflsad
MUL M(X)
DIV M(X); JUMP M(X,0:19)
JUMP M(X,20:39) ; JUMP+ M(X,0:19)
JUMP+ M(X,20:39) ; STOR M(X,8:19)
STOR M(X,28:39) ; LSH
RSH ; STOR M(X)