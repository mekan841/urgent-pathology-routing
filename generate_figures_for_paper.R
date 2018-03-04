
library(ggmap)
library(ggplot2)
library(data.table)


INPUT_FILE_1 = ''
INPUT_FILE_2 = ''

d <- read.table(INPUT_FILE_1, sep=',', header = TRUE)

ggplot(head(d,50), aes(x = reorder(Origin.Address, Trip.Count), y = Trip.Count)) +
        geom_bar(stat = "identity") +
        coord_flip() +
        ggtitle("Trip Counts by Origin Address") +
        labs(y = "Trip Count") + 
        labs(x = "Origin Address")

d <- read.table(INPUT_FILE_2, sep=',', header = TRUE)

ggplot(d, aes(x = thehour, y = cnt)) +
        geom_bar(stat = "identity") +
        ggtitle("Trip Counts by Hour of Day") +
        labs(y = "Trip Count") + 
        labs(x = "Hour of Day")


FILE = ''
OUTPUT_PDF = ''

data <- fread(FILE)
chch_map <- get_map("Christchurch, New Zealand", zoom=12, color='bw')

pdf(OUTPUT_PDF, width=6, height=4, paper='special')
p <- ggmap(chch_map)
p <- p + geom_point(data=data, aes(x=lng, y=lat, size=data$spreadsheet_header_1), color="red", alpha=0.8) + scale_size(range = c(0, 8))
dev.off()

scale_fill_gradientn(colours=rev(rainbow(100, start=0, end=0.75))) + 
stat_density2d(data=data, aes(x = lng, y = lat, fill = ..level..,alpha=..level..), geom = 'polygon') +
scale_alpha_continuous(guide="none",range=c(0,0.3))

