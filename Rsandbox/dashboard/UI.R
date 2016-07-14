library(shiny)
library(shinydashboard)
library(httr)
library(leaflet)


header <- dashboardHeader()

sidebar <- dashboardSidebar(
    sidebarMenu(
        menuItem("Tab 1", tabName = "Tab 1", icon = icon("check-circle"), badgeLabel = "testing", badgeColor = "red"),
        menuItem("Tab 2", tabName = "Tab 2", icon = icon("database"), badgeLabel = "production", badgeColor = "blue")
    )
)
body <- dashboardBody(
    fluidRow(
        column(width = 7,
               box(width = NULL, solidHeader = TRUE,
                   verbatimTextOutput("SampleDataFrame")
               )
        ),
        column(width = 3,
               box(width = NULL, status = "warning",
                   selectInput("interval", "Refresh interval",
                               choices = c(
                                   "30 seconds" = 30,
                                   "1 minute" = 60,
                                   "2 minutes" = 120,
                                   "5 minutes" = 300,
                                   "10 minutes" = 600
                               ),
                               selected = "60"
                   ),
                   uiOutput("timeSinceLastUpdate"),
                   actionButton("refresh", "Refresh now"),
                   p(class = "text-muted",
                     br(),
                     "Source data updates every 30 seconds."
                   )
               )
        )
    )
)


dashboardPage(
    skin="black",
    dashboardHeader(title = "Example"),
    sidebar,
    body
)