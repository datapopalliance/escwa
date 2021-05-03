####### BSTS Analysis for Google Trends Keywords and Unemployment Rate ######
####### Allowing system to work with Arabic keywords ########################
Sys.setlocale("LC_CTYPE", "arabic")
####### Check and Install required packages #################################
list.of.packages <- c("pacman")
new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)
library(pacman) # Wrapper for install and library in one command
#Installing and loading required packages
p_load(tidyverse, bsts, zoo, tempdisagg, lubridate) 
####### Data Preparation #####################################################
####### Step 1: Importing data sets ##########################################
####### Initial data ########################################################
# The first file should be a csv file that contains quarterly data
# for unemployment rates. The file should contain two columns
# The first column is called Index is contains dates in the following 
# format (YYYY-Q) The year should be such as 2010, 2011, etc. 
# and the Quarter Q should be the number of the quarter 1, 2, 3, 4 
# in that given year.

# Unemployment rate data set
UER <- read_csv("D:/Projects/DPA/Jordan/gt_unemp.csv")
# Monthly scrapped keywords
MKW <- read_csv("D:/Projects/DPA/Jordan/Keywords_monthly.csv")
# Quarterly scrapped keywords
QKW <- read_csv("D:/Projects/DPA/Jordan/Qkeywords.csv")

##### Step 2: Disaggregating quarterly UER to monthly level #################
# The disaggregation process assumes the change within quarter is 
# evenly distributed. For instance, the unemployment increased 3% from quarter
# to the quarter after. Then each month in the next quarter is assumed 
# to contribute 1%.

tsdig <- read.zoo(UER, FUN = function(x) as.yearqtr(x, "%Y-%q"))
UERM_I <- zooreg(na.approx(c(t(cbind(tsdig, NA, NA)))),
                 start = as.yearmon(start(tsdig)), freq = 12)
UERM <- fortify.zoo(UERM_I) #data set of unemployment rate

# Cleaning unnecessary objects
rm(list.of.packages)
rm(new.packages)
rm(tsdig)
rm(UERM_I)

##### Step 3: Cleaning keywords from excess zeros and small values cells ####
MKW <- MKW[,colMeans(MKW == 0) <= 0.1]
QKW <- QKW[,colMeans(QKW == 0) <= 0.1]

##### Step 4: Splitting Keywords into training and prediction data ##########
# Creating Training Data sets
QKWT <- QKW[1:length(UER$Quarter),]
MKWT <- MKW[1:length(UERM$Index),]

# Creating Prediction data sets
QKWP <- anti_join(QKW, QKWT)
MKWP <- anti_join(MKW, MKWT)

##### Converting Dates UER and UERM using lubridate package #################
UER$Quarter <- yq(UER$Quarter)
UERM$Index <- my(UERM$Index)

################### Step 5: Applying BSTS for the training data ##############

if (forecast::nsdiffs(ts(UER$Unemp_dos, frequency = 4, 
                         start = c(2010,1))) == 1) {
  
  ss <- AddSeasonal(ss, UER, nseasons = 4)
  
}


ss <- AddLocalLinearTrend(list(), UER$Unemp_dos)

model1 <- bsts(UER$Unemp_dos,
               
               state.specification = ss,
               
               niter = 1000)


model2 <- bsts(UER$Unemp_dos ~ .,
               
               state.specification = ss,
               
               niter = 1000,
               
               data = QKWT)

### Create a png file

png("ModCompQ.png")

CompareBstsModels(list("No Google Trends" = model1,
                       "With Google Trends" = model2),
                  colors = c("blue", "red"),
                  xlab = "Time: Number of Quarters in the time series",
                  main = "Comparison between predictions using BSTS\n with and without Google Trends")

dev.off() # Close the png plot

predict1 <- predict(model1, horizon = 2)

predict2 <- predict(model1, horizon = 2, newdata = QKWP)

par(mfrow = c(1,2))

plot(as.ts(UER$Unemp_dos), 
     ylim = c(10,max(UER$Unemp_dos) + 10), 
     main = "Actual Unemployment rate",
     xlab = " Actual Reported Unemployment rates at each Quarter by JDoS",
     ylab = "Unemployment rate")


plot(predict1, 
     ylim = c(10,max(UER$Unemp_dos) + 10),
     main = "Predicted Unemployment rates \nfor the next two Quarters",
     ylab = "Unemployment rate")


plot(as.ts(UER$Unemp_dos), ylim = c(10,max(UER$Unemp_dos) + 10), 
     main = "Actual Unemployment rate",
     ylab = "Unemployment rate")

plot(predict2, ylim = c(10, max(UER$Unemp_dos) + 10),
     main = "Predicted Unemployment rates \nfor the next two Quarters",
     ylab = "Unemployment rate")


NGTpredQ <- data.frame(Median = round(predict1$median,2),
                       Mean = round(predict1$mean,2),
                       t(round(predict1$interval,2)))

names(NGTpredQ)[names(NGTpredQ) == "X2.5."] <- "Lower Bound"
names(NGTpredQ)[names(NGTpredQ) == "X97.5."] <- "Upper Bound"


data.frame(round(predict2$interval,2))

GTpredQ <- data.frame(Median = round(predict2$median,2),
                      Mean = round(predict2$mean,2),
                      t(round(predict2$interval,2)))

names(GTpredQ)[names(GTpredQ) == "X2.5."] <- "Lower Bound"
names(GTpredQ)[names(GTpredQ) == "X97.5."] <- "Upper Bound"


### Data frame for the data without GT

QFSNGT <- as.vector(c(as.numeric(predict1[["original.series"]]),round(predict1$mean,2)))
QFSNGTL <- as.vector(c(as.numeric(predict1[["original.series"]]),
                       round(predict1$interval[1,],2)))
QFSNGTU <- as.vector(c(as.numeric(predict1[["original.series"]]),
                       round(predict1$interval[2,],2)))
QNGT_DF <- data.frame(seq(ymd("2010/1/1"), by = "quarter",
                          length.out = length(QFSNGT)), 
                      QFSNGT, QFSNGTL, QFSNGTU)

names(QNGT_DF)[names(QNGT_DF) == "seq.ymd..2010.1.1....by....quarter...length.out...length.QFSNGT.."] <- "Quarter"
names(QNGT_DF)[names(QNGT_DF) == "QFSNGT"] <- "Unemployment Rate and Predictions"
names(QNGT_DF)[names(QNGT_DF) == "QFSNGTL"] <- "Unemployment Rate and lower Bound"
names(QNGT_DF)[names(QNGT_DF) == "QFSNGTU"] <- "Unemployment Rate and Upper Bound"

### Data frame for the data with GT

QFSGT <- as.vector(c(as.numeric(predict2[["original.series"]]),round(predict2$mean,2)))
QFSGTL <- as.vector(c(as.numeric(predict2[["original.series"]]),
                      round(predict2$interval[1,],2)))
QFSGTU <- as.vector(c(as.numeric(predict2[["original.series"]]),
                      round(predict2$interval[2,],2)))
QGT_DF <- data.frame(seq(ymd("2010/1/1"), by = "quarter",
                         length.out = length(QFSGT)), 
                     QFSGT, QFSGTL, QFSGTU)

names(QGT_DF)[names(QGT_DF) == "seq.ymd..2010.1.1....by....quarter...length.out...length.QFSGT.."] <- "Quarter"
names(QGT_DF)[names(QGT_DF) == "QFSGT"] <- "Unemployment Rate and Predictions"
names(QGT_DF)[names(QGT_DF) == "QFSGTL"] <- "Unemployment Rate and lower Bound"
names(QGT_DF)[names(QGT_DF) == "QFSGTU"] <- "Unemployment Rate and Upper Bound"

rm(QFSGT)
rm(QFSGTL)
rm(QFSGTU)
rm(QFSNGT)
rm(QFSNGTL)
rm(QFSNGTU)

############### BSTS Prediction ##########################


if (forecast::nsdiffs(ts(UERM$Index, frequency = 12, 
                         start = c(2010,1))) == 1) {
  
  ss <- AddSeasonal(ss, UERM, nseasons = 12)
  
}


ss <- AddLocalLinearTrend(list(), UERM$UERM_I)

model_month1 <- bsts(UERM$UERM_I,
                     
                     state.specification = ss,
                     
                     niter = 1000)


model_month2 <- bsts(UERM$UERM_I ~ .,
                     
                     state.specification = ss,
                     
                     niter = 1000,
                     
                     data = MKWT)

#### open a png file to save the plot produced
png("ModCompM.png")

CompareBstsModels(list("No Google Trends" = model_month1,
                       "With Google Trends" = model_month2),
                  colors = c("blue", "red"),
                  xlab = "Time: Number of Months in the time series",
                  main = "Comparison between predictions using BSTS\n with and without Google Trends")

dev.off() #closing the png plot

predict_month1 <- predict(model_month1, horizon = 5)

predict_month2 <- predict(model_month2, horizon = 5, newdata = MKWP)


par(mfrow = c(1,2))


plot(as.ts(UERM$UERM_I), 
     ylim = c(10,max(UERM$UERM_I) + 10), 
     main = "Actual Unemployment rate",
     ylab = "Unemployment rate")


plot(predict_month1, 
     ylim = c(10,max(UERM$UERM_I) + 10),
     main = "Predicted Unemployment rates \nfor six months",
     ylab = "Unemployment rate")


plot(as.ts(UERM$UERM_I), ylim = c(10,max(UERM$UERM_I) + 10),
     main = "Actual Unemployment rate",
     ylab = "Unemployment rate")

plot(predict_month2, 
     ylim = c(10, max(UERM$UERM_I) + 10),
     main = "Predicted Unemployment rates \nfor six months",
     ylab = "Unemployment rate")


NGTpredM <- data.frame(Median = round(predict_month1$median,2),
                       Mean = round(predict_month1$mean,2),
                       t(round(predict_month1$interval,2)))

names(NGTpredM)[names(NGTpredM) == "X2.5."] <- "Lower Bound"
names(NGTpredM)[names(NGTpredM) == "X97.5."] <- "Upper Bound"

GTpredM <- data.frame(Median = round(predict_month2$median,2),
                      Mean = round(predict_month2$mean,2),
                      t(round(predict_month2$interval,2)))

names(GTpredM)[names(GTpredM) == "X2.5."] <- "Lower Bound"
names(GTpredM)[names(GTpredM) == "X97.5."] <- "Upper Bound"

### Data frame for the data without GT

MFSNGT <- as.vector(c(as.numeric(predict_month1[["original.series"]]),
                      round(predict_month1$mean,2)))
MFSNGTL <- as.vector(c(as.numeric(predict_month1[["original.series"]]),
                       round(predict_month1$interval[1,],2)))
MFSNGTU <- as.vector(c(as.numeric(predict_month1[["original.series"]]),
                       round(predict_month1$interval[2,],2)))
MNGT_DF <- data.frame(seq(ymd("2010/1/1"), by = "month",
                          length.out = length(MFSNGT)), 
                      MFSNGT, MFSNGTL, MFSNGTU)

names(MNGT_DF)[names(MNGT_DF) == "seq.ymd..2010.1.1....by....month...length.out...length.MFSNGT.."] <- "Month"
names(MNGT_DF)[names(MNGT_DF) == "MFSNGT"] <- "Unemployment Rate and Predictions"
names(MNGT_DF)[names(MNGT_DF) == "MFSNGTL"] <- "Unemployment Rate and lower Bound"
names(MNGT_DF)[names(MNGT_DF) == "MFSNGTU"] <- "Unemployment Rate and Upper Bound"


### Data frame for the data with GT

MFSGT <- as.vector(c(as.numeric(predict_month2[["original.series"]]),
                     round(predict_month2$mean,2)))
MFSGTL <- as.vector(c(as.numeric(predict_month2[["original.series"]]),
                      round(predict_month2$interval[1,],2)))
MFSGTU <- as.vector(c(as.numeric(predict_month2[["original.series"]]),
                      round(predict_month2$interval[2,],2)))
MGT_DF <- data.frame(seq(ymd("2010/1/1"), by = "month",
                         length.out = length(MFSGT)), 
                     MFSGT, MFSGTL, MFSGTU)

names(MGT_DF)[names(MGT_DF) == "seq.ymd..2010.1.1....by....month...length.out...length.MFSGT.."] <- "Month"
names(MGT_DF)[names(MGT_DF) == "MFSNGT"] <- "Unemployment Rate and Predictions"
names(MGT_DF)[names(MGT_DF) == "MFSNGTL"] <- "Unemployment Rate and lower Bound"
names(MGT_DF)[names(MGT_DF) == "MFSNGTU"] <- "Unemployment Rate and Upper Bound"

rm(MFSGT)
rm(MFSGTL)
rm(MFSGTU)
rm(MFSNGT)
rm(MFSNGTL)
rm(MFSNGTU)

########### Export the outcomes to csv files ###################################
### Point prediction and Credibility Intervals data
# Quarterly Data points
write_csv(NGTpredQ, "Point Estimations Quarterly No GT.csv")
write_csv(GTpredQ, "Point Estimations Quarterly with GT.csv")

# Monthly Data points
write_csv(NGTpredM, "Point Estimations Monthly No GT.csv")
write_csv(NGTpredM, "Point Estimations Monthly with GT.csv")


### Outcomes of the prediction models as csv files for plotting
write_csv(QNGT_DF, "Quarterly Data No GT.csv")
write_csv(QGT_DF, "Quarterly Data with GT.csv")
write_csv(MNGT_DF, "Monthly Data No GT.csv")
write_csv(MGT_DF, "Monthly Data with GT.csv")
