pdf("k.pdf", width=6, height=4)

# Define 2 vectors
acc <- c(0.425197,
         0.449612,
         0.473282,
         0.496241,
         0.496241,
         0.496241,
         0.347107,
         0.507463,
         0.518519,
         0.360656,
         0.518519,
         0.518519)

plot(acc, type="o", col="blue", ylim=c(0.3,0.55), axes=FALSE, ann=FALSE)


axis(1, at=1:12, lab=1:12)
axis(2, at=0.3+(0.05*0:5))

title(xlab="k")
title(ylab="F-score")

dev.off()
