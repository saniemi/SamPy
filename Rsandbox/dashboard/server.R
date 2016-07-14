source('helper_functions.R')

shinyServer(function(input, output, session) {

    readData <- reactivePoll(2000, session, getDataUpdate, getData)

    output$timeSinceLastUpdate <- renderText(format(readData()$hello[1]))

    output$SampleDataFrame <- renderText({text <- readData()$msg
                                          paste(text, collapse = '\n')})

})
