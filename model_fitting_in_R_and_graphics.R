
install.packages("data.table")
savehistory(file = "/tmp/.Rhistory")

require(data.table)
require(cowplot)
library(ggfortify)
library(car)


a <- read.table('/path/to/dataset_one_file_for_R_input_for_validating_cost_model_on_older_data.csv', header=TRUE, sep=",")
fit1 <- lm(Fare ~ JobDistance + WaitingTime + CarTravellingTime, data=a)
summary(fit1)
fit2 <- lm(Fare ~ JobDistance + CarTravellingTime, data=a)
summary(fit2)
fit2a <- lm(Fare ~ JobDistance + CarTravellingTime + 0, data=a)
summary(fit2a)
fit3 <- lm(Fare ~ JobDistance, data=a)
summary(fit3)

anova(fit1, fit2)
anova(fit1, fit3)
layout(matrix(c(1,2,3,4),2,2))
plot(fit1)

# coefficients(fit2)
# a$fittedValues <- fitted(fit2)
# write.table(a, file='/tmp/fitted.csv')

# tiff("./google_maps_linear_fit.tiff", width=3.5, height=3.5, units="in", res=300)
# plot(b$origin_to_lab_times, b$CarTravellingTime, ylab="Known Travelling Time (min)", xlab="Estimated Travelling Time (min)")
# # abline(a,b, lty=2, lwd=3)
# abline(fitb, col="black", lwd=3)
# dev.off()

require(data.table)
b <- read.table('/path/to/dataset_one_file_for_R_input_for_validating_cost_model_on_older_data_geocoded_cleaned_reduced_compare_google_maps_times.csv', header=TRUE, sep=",")
fitb <- lm(CarTravellingTime ~ origin_to_lab_times, data=b)
summary(fitb)
fitbb <- lm(JobDistance ~ origin_to_lab_distances, data=b)
summary(fitbb)

# tiff("estimation_quality_plot_just_time.tiff", width=5.09, height=5.09, units="in", res=300)
# par(pty="s")
# avPlot(fitb, "origin_to_lab_times", main="", xlab="", ylab="", col.lines="black", cex=0.6, xaxp  = c(-10, 30, 4), yaxp  = c(-10, 30, 4), asp=1)
# # avPlot(fitb, "(Intercept)", "intercept", main="", xlab="", ylab="", col.lines="black", cex=0.6)
# title(xlab="Estimated Time | intercept", ylab="True Time | intercept") 
# # plot(b$origin_to_lab_times, b$CarTravellingTime, panel.first=grid(lty=1), cex=0.6, xlim=c(0, 30), ylim=c(0, 30), ylab="True Time (min)", xlab="Estimated Time (min)")
# # abline(fitb)
# dev.off()
# system("convert time_quality_plot.tiff -resize 1050x1050 -density 300 -units PixelsPerInch time_quality_plot.tiff")

tiff("estimation_quality_plot_both_1.tiff", width=4, height=4, units="in", res=300)
avPlot(fitb, "origin_to_lab_times", main="", xlab="", ylab="", col.lines="black", cex=0.6, asp=1)
# av <- recordPlot()
# axis(1, family="serif") # at=x, label=x, tick=F, 
# axis(2, family="serif") # at=seq(1,6,1), label=sprintf("$%s", seq(300,400,20)), tick=F, las=2, 
title(xlab="Estimated Time | intercept", ylab="True Time | intercept") 
dev.off()
system("convert ./estimation_quality_plot_both_1.tiff -resize 825x825 -density 300 -units PixelsPerInch ./estimation_quality_plot_both_1.tiff") # 1050 x 1050

tiff("estimation_quality_plot_both_2.tiff", width=4, height=4, units="in", res=300)
# par(pty="s")
avPlot(fitbb, "origin_to_lab_distances", main="", xlab="", ylab="", col.lines="black", cex=0.6, asp=1  )
# av <- recordPlot()
# axis(1, family="serif") # at=x, label=x, tick=F, 
# axis(2, family="serif") # at=seq(1,6,1), label=sprintf("$%s", seq(300,400,20)), tick=F, las=2, 
axis(1, )
title(xlab="Estimated Distance | intercept", ylab="True Distance | intercept") 
dev.off()
system("convert ./estimation_quality_plot_both_2.tiff -resize 825x825 -density 300 -units PixelsPerInch ./estimation_quality_plot_both_2.tiff") # 1050 x 1050
system("convert +append estimation_quality_plot_both_1.tiff estimation_quality_plot_both_2.tiff estimation_quality_plot_both_3.tiff")
# scale image in GGPLOT to 1650 wide

# can put this in for custom gridlines
# axis(1, at = c(5,10,20))
# panel.first=c(abline(v=c(-5,5,15,25), col='lightgrey'),abline(v=c(-5,5,15,25), col='lightgrey'))   #, lty = 3

# png("cost_residuals.png", width=8, height=8, units="in", res=300)
# layout(matrix(c(1,2,3,4),2,2))
# plot(fit2)
# dev.off()

tiff("partial_plot_cost_model_1.tiff", width=4, height=4, units="in", res=300)
avPlot(fit2, "CarTravellingTime", main="", xlab="", ylab="", col.lines="black", cex=0.6, asp=1)
# av <- recordPlot()
# axis(1, family="serif") # at=x, label=x, tick=F, 
# axis(2, family="serif") # at=seq(1,6,1), label=sprintf("$%s", seq(300,400,20)), tick=F, las=2, 
title(xlab="Journey Time | others", ylab="Fare | others") 
dev.off()
system("convert ./partial_plot_cost_model_1.tiff -resize 825x825 -density 300 -units PixelsPerInch ./partial_plot_cost_model_1.tiff") # 1050 x 1050

tiff("partial_plot_cost_model_2.tiff", width=4, height=4, units="in", res=300)
avPlot(fit2, "JobDistance", main="", xlab="", ylab="", col.lines="black", cex=0.6, asp=1)
# av <- recordPlot()
# axis(1, family="serif") # at=x, label=x, tick=F, 
# axis(2, family="serif") # at=seq(1,6,1), label=sprintf("$%s", seq(300,400,20)), tick=F, las=2, 
title(xlab="Journey Distance | others", ylab="Fare | others") 
dev.off()
system("convert ./partial_plot_cost_model_2.tiff -resize 825x825 -density 300 -units PixelsPerInch ./partial_plot_cost_model_2.tiff") # 1050 x 1050
system("convert +append partial_plot_cost_model_1.tiff partial_plot_cost_model_2.tiff partial_plot_cost_model_3.tiff")
# scale image in GGPLOT to 1650 wide

addresses1 <- c("address1", "address2", ...)
counts1 <- c(0, 0, ...)

# lty.o <- par("lty")
# par(lty = 0)
# par(lty = lty.o)
tiff("bar_plot.tiff", width=5.09, height=5.09, units="in", res=300)
barplot(counts1[0:10], main="", xlab="", ylab="Requests during Feb-Jun 2017", space = 0.1, border=NA, names.arg=c("Clinic 1", "Clinic 2", "Clinic 3", "Clinic 4", "Clinic 5", "Clinic 6", "Clinic 7", "Clinic 8","Clinic 9","Clinic 10"), las=2) 
dev.off()
system("convert bar_plot.tiff -resize 1050x1050 -density 300 -units PixelsPerInch bar_plot.tiff")

e <- autoplot(fit2)
ggsave("cost_model_residuals_standalone.tiff", e, units="in", width=5.5, height=5.5, dpi=300, compression = 'lzw')
#resize to 1050 in GIMP

# resize to 900 in GIMP
# convert +append distance_and_waitTime_relationship_to_Fare.tiff cost_model_residuals_900_for_appending_to_double_cost_relationship_plot.tiff  three_cost_plot.tiff
# write in a letter C


# tiff("./google_maps_residuals.tiff", width=6, height=6, units="in", res=300)
# par(mar=c(5,4,2,2)+0.1)     # bottom, left, top, and right, default 5,4,4,?
# layout(matrix(c(1,2,3,4),2,2))
# plot(fitb)
# dev.off()


tiff("./cost_linear_fit.tiff", width=5.51, height=3, units="in", res=300)
layout(matrix(c(1,2),1,2))
par(mar=c(5,4,2,1)+0.1)     # bottom, left, top, and right, default 5,4,4,?

plot(a$JobDistance, a$Fare, ylab="Fare", xlab="Distance (km)")#, xlim=c(0, 30), ylim=c(0, 30)) 
# axis(1, at=c(0, 10, 20, 30), labels=c(0, 10, 20, 30))
axis(2, at=c(0, 20, 40, 60, 80), labels=c(0, 20, 40, 60, 80))

par(mar=c(5,4,2,1)+0.1)     # bottom, left, top, and right, default 5,4,4,?
plot(a$WaitingTime, a$Fare, ylab="Fare", xlab="Waiting Time (min)")#, xlim=c(0, 30), ylim=c(0, 30))
axis(2, at=c(0, 20, 40, 60, 80), labels=c(0, 20, 40, 60, 80))
# abline(a,b, lty=2, lwd=3)
# abline(fitb, col="red", lwd=3)
dev.off()


p11 <- ggplot(a, aes(x=JobDistance, y=Fare)) + geom_point(shape=1)
# p11 <- p11 + coord_fixed() # + theme(aspect.ratio=1)
p11 <- p11 + scale_x_continuous(name = "Distance (km)") + #, limits = c(0, 30)) +
	scale_y_continuous(name = "Fare") #, limits = c(0, 30))
p11 <- p11 + theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "black"))
# p11 <- p11 + theme(text = element_text(size=10),
#         axis.text.x = element_text(angle=0, hjust=1)) 
p11


p12 <- ggplot(a, aes(x=WaitingTime, y=Fare)) + geom_point(shape=1)
# p11 <- p11 + coord_fixed() # + theme(aspect.ratio=1)
p12 <- p12 + scale_x_continuous(name = "Waiting Time (min)") + #, limits = c(0, 30)) +
	scale_y_continuous(name = "Fare") #, limits = c(0, 30))
p12 <- p12 + theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank(), axis.line = element_line(colour = "black"))
# p11 <- p11 + theme(text = element_text(size=10),
#         axis.text.x = element_text(angle=0, hjust=1)) 
p12


x <- plot_grid(p11, p12, align='h', labels=c('A', 'B'))
ggsave("distance_and_waitTime_relationship_to_Fare.tiff", x,  units="in", width=5.51, height=3, dpi=300, compression = 'lzw')


layout(matrix(c(1,2,3,4),2,2))
plot(fitb)
#z <- recordPlot()
z <- autoplot(fitb)

p11 <- ggplot(b, aes(x=origin_to_lab_times, y=CarTravellingTime)) + geom_point(shape=1) + geom_smooth(method=lm, se=FALSE, color="black")
p11 <- p11 + coord_fixed() # + theme(aspect.ratio=1)
p11 <- p11 + scale_x_continuous(name = "Estimated Travelling Time (min)", limits = c(0, 30)) +
      scale_y_continuous(name = "Known Travelling Time (min)", limits = c(0, 30))
p11 <- p11 + theme_bw() + theme(panel.border = element_blank(), panel.grid.major = element_blank(),
panel.grid.minor = element_blank(), axis.line = element_line(colour = "black"))
# p11 <- p11 + theme(text = element_text(size=10),
#         axis.text.x = element_text(angle=0, hjust=1)) 

p11
ggsave("time_fit_standalone.tiff", p11, units="in", width=3.5, height=3.5, dpi=300, compression = 'lzw')


p11a <- p11 + theme(text = element_text(size=8),
        axis.text.x = element_text(angle=0, hjust=1)) 
ggsave("time_fit_sub1.tiff", p11a, units="in", width=2.6, height=2.6, dpi=300, compression = 'lzw')
# z2 <- plot_grid(p11a, z, align='h', labels=c('A', 'B'))
ggsave("time_residuals_sub2.tiff", z, units="in", width=5.5, height=5.5, dpi=300, compression = 'lzw')
# convert +append cost_model_fit_sub*.tiff out.tiff
# edit with GGplot to get A and B on figure from distance_and_waittime plot

