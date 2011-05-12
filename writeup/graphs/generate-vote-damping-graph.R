pdf("damping.pdf", width=6, height=4)

# Define 2 vectors
acc <- c(0.373984,
         0.360656,
         0.360656,
         0.387097,
         0.400000,
         0.412698,
         0.400000,
         0.400000,
         0.387097,
         0.373984)


# Graph cars using a y axis that ranges from 0 to 12
plot(acc, type="o", col="blue", ylim=c(0.3,0.5), axes=FALSE, ann=FALSE)


axis(1, at=0:10, lab=0.1*0:10)
axis(2, at=0.3+(0.04*0:5))

title(xlab="Vote Damping Coefficient")
title(ylab="F-score")

dev.off()
