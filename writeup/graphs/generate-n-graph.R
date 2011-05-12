pdf("n.pdf", width=6, height=4)

# Define 2 vectors
acc <- c(0.373984,
         0.347107,
         0.373984,
         0.449612,
         0.412698,
         0.437500,
         0.437500)


# Graph cars using a y axis that ranges from 0 to 12
plot(acc, type="o", col="blue", ylim=c(0.3,0.5), axes=FALSE, ann=FALSE)


axis(1, at=1:7, lab=2*2:8)
axis(2, at=0.3+(0.04*0:5))

title(xlab="n")
title(ylab="F-score")

dev.off()
