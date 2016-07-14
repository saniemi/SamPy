library(lubridate)
library(bsts)
library(dplyr)
library(ggplot2)

### Load the data
data("AirPassengers")
Y <- window(AirPassengers, start=c(1949, 1), end=c(1959,12))
y <- log10(Y)


### Run the bsts model
ss <- AddLocalLinearTrend(list(), y)
ss <- AddSeasonal(ss, y, nseasons=12)
bsts.model <- bsts(y, state.specification=ss, niter=200000, timeout.seconds=5*60)

### Get a suggested number of burn-ins
burn <- SuggestBurn(0.15, bsts.model)

### Predict
p <- predict.bsts(bsts.model, horizon = 12, burn = burn, quantiles = c(.025, .975))

### Actual versus predicted
d2 <- data.frame(
    # fitted values and predictions
    c(10^as.numeric(-colMeans(bsts.model$one.step.prediction.errors[-(1:burn),])+y),
      10^as.numeric(p$mean)),
    # actual data and dates
    as.numeric(AirPassengers),
    as.Date(time(AirPassengers)))
names(d2) <- c("Fitted", "Actual", "Date")

### MAPE (mean absolute percentage error)
MAPE <- filter(d2, year(Date)>1959) %>% summarise(MAPE=mean(abs(Actual-Fitted)/Actual))

### 95% forecast credible interval
posterior.interval <- cbind.data.frame(
    10^as.numeric(p$interval[1,]),
    10^as.numeric(p$interval[2,]),
    subset(d2, year(Date)>1959)$Date)
names(posterior.interval) <- c("LL", "UL", "Date")

### Join intervals to the forecast
d3 <- left_join(d2, posterior.interval, by="Date")

### Plot actual versus predicted with credible intervals for the holdout period
ggplot(data=d3, aes(x=Date)) +
    geom_line(aes(y=Actual, colour = "Actual"), size=1.2) +
    geom_line(aes(y=Fitted, colour = "Fitted"), size=1.2, linetype=2) +
    theme_bw() + theme(legend.title = element_blank()) + ylab("") + xlab("") +
    geom_vline(xintercept=as.numeric(as.Date("1959-12-01")), linetype=2) +
    geom_ribbon(aes(ymin=LL, ymax=UL), fill="grey", alpha=0.5) +
    ggtitle(paste0("BSTS -- Holdout MAPE = ", round(100*MAPE,2), "%")) +
    theme(axis.text.x=element_text(angle = -90, hjust = 0))

### Extract the components
components <- cbind.data.frame(
    colMeans(bsts.model$state.contributions[-(1:burn),"trend",]),
    colMeans(bsts.model$state.contributions[-(1:burn),"seasonal.12.1",]),
    as.Date(time(Y)))
names(components) <- c("Trend", "Seasonality", "Date")
components <- melt(components, id="Date")
names(components) <- c("Date", "Component", "Value")

### Plot
ggplot(data=components, aes(x=Date, y=Value)) + geom_line() +
    theme_bw() + theme(legend.title = element_blank()) + ylab("") + xlab("") +
    facet_grid(Component ~ ., scales="free") + guides(colour=FALSE) +
    theme(axis.text.x=element_text(angle = -90, hjust = 0))
