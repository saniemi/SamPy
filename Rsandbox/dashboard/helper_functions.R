library(jsonlite)
library(rkafka)

getKafkaUpdate <- function(){
    consumer <- rkafka.createConsumer("127.0.0.1:2181", 'gasStation',
                                      consumerTimeoutMs="500")
    data <- rkafka.read(consumer)
    rkafka.closeConsumer(consumer)

    if (length(data) > 0){
        return(Sys.time())}
    else {return("")}

}

getKafka <- function(){
    consumer <- rkafka.createConsumer("127.0.0.1:2181", 'gasStation')
    data <- rkafka.read(consumer)
    rkafka.closeConsumer(consumer)
    return(data)
}

getDataUpdate <- function(){
    URL = "http://127.0.0.1:5000/update/"
    data <- fromJSON(URL)
    return(data$msg)
}

getData <- function() {
    URL = "http://127.0.0.1:5000/"
    time <- fromJSON(URL)

    URL = "http://127.0.0.1:5000/stream/"
    data <- fromJSON(URL)

    if (length(data$msg) < 1){
        data = 'no new'
    }

    results <- data.frame(time, data)

    return(results)
}

getTime <- function(){
    URL = "http://127.0.0.1:5000/"
    time <- fromJSON(URL)
    return(time$hello)
}
