library(lubridate)
library(bsts)
library(ggplot2)
library(reshape2)

### Fit the model with regressors
data(iclaims)
ss <- AddLocalLinearTrend(list(), initial.claims$iclaimsNSA)
ss <- AddSeasonal(ss, initial.claims$iclaimsNSA, nseasons=52)
bsts.reg <- bsts(iclaimsNSA ~ ., state.specification = ss, data =
                     initial.claims, niter=10000, timeout.seconds=5*60)

### Get the number of burn-ins to discard
burn <- SuggestBurn(0.1, bsts.reg)

### Helper function to get the positive mean of a vector
PositiveMean <- function(b) {
    b <- b[abs(b) > 0]
    if (length(b) > 0)
        return(mean(b))
    return(0)
}

### Get the average coefficients when variables were selected (non-zero slopes)
coeff <- data.frame(melt(apply(bsts.reg$coefficients[-(1:burn),], 2, PositiveMean)))
coeff$Variable <- as.character(row.names(coeff))
ggplot(data=coeff, aes(x=Variable, y=value)) +
    geom_bar(stat="identity", position="identity") +
    theme(axis.text.x=element_text(angle = -90, hjust = 0)) +
    xlab("") + ylab("") + ggtitle("Average coefficients")

### Inclusion probabilities -- i.e., how often were the variables selected
inclusionprobs <- melt(colMeans(bsts.reg$coefficients[-(1:burn),] != 0))
inclusionprobs$Variable <- as.character(row.names(inclusionprobs))
ggplot(data=inclusionprobs, aes(x=Variable, y=value)) +
    geom_bar(stat="identity", position="identity") +
    theme(axis.text.x=element_text(angle = -90, hjust = 0)) +
    xlab("") + ylab("") + ggtitle("Inclusion probabilities")

### Get the components
components.withreg <- cbind.data.frame(
    colMeans(bsts.reg$state.contributions[-(1:burn),"trend",]),
    colMeans(bsts.reg$state.contributions[-(1:burn),"seasonal.52.1",]),
    colMeans(bsts.reg$state.contributions[-(1:burn),"regression",]),
    as.Date(time(initial.claims)))
names(components.withreg) <- c("Trend", "Seasonality", "Regression", "Date")
components.withreg <- melt(components.withreg, id.vars="Date")
names(components.withreg) <- c("Date", "Component", "Value")

ggplot(data=components.withreg, aes(x=Date, y=Value)) + geom_line() +
    theme_bw() + theme(legend.title = element_blank()) + ylab("") + xlab("") +
    facet_grid(Component ~ ., scales="free") + guides(colour=FALSE) +
    theme(axis.text.x=element_text(angle = -90, hjust = 0))
