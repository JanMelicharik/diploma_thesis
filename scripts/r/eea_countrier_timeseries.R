rm(list=ls())

library(ggplot2)
library(plyr)
library(readr)
library(stringr)
library(tibble)


OUTPUT_BY_COUNTRY_DATA_PATH <- paste(getwd(), "/data/output/by_country", sep = "")
lockdowns_path <- "/Users/janmelicharik/Documents/Diplomka/data/output/lockdowns.csv"

lockdowns_data <- read_delim(lockdowns_path, delim=",")

for (country_path in Sys.glob(file.path(OUTPUT_BY_COUNTRY_DATA_PATH, "**/timeseries_weekly.csv")))
{
  country_code <- str_split(country_path, "/")[[1]][9]
  data <- read_delim(country_path, delim=",")
  # NA values replaced by zeros - missing values from original data correspond
  # to periods with very little or zero new COVID-19 cases or deaths
  data[is.na(data["deaths"]), "deaths"] <- 0
  data[is.na(data["covid_cases"]), "covid_cases"] <- 0
  # Indexed values - multiplied to scale 100
  data["bookings"] <- data["bookings"] * 100
  data["cancellations"] <- data["cancellations"] * 100
  # By definition there should not be negative values, in case there are
  # it's a mistake in data input for the source and is replaced with
  # absolute value
  if (any(data < 0)) {
    data[data<0] <- abs(data[data<0])
  }
  # Calculation of scaling constant for right y axis (COVID-19 cases and deaths)
  max_index <- max(data$bookings, data$cancellations)
  max_cases <- max(data$covid_cases, data$deaths)
  upper_bound_left_y <- round_any(max_index, 10, ceiling) + 10
  upper_bound_right_y <- round_any(max_cases, 500, ceiling) + 500
  
  scaling_cofficient <- upper_bound_left_y / upper_bound_right_y
  
  data["covid_cases"] <- data["covid_cases"] * scaling_cofficient
  data["deaths"] <- data["deaths"] * scaling_cofficient
  
  plt <- ggplot(data, aes(x=date)) +
    geom_area(aes(y=covid_cases), color="orangered", fill="orangered", alpha=.1, size=0.55) +
    geom_area(aes(y=deaths), color="grey0", fill="grey0", alpha=.1, size=0.55) +
    geom_area(aes(y=cancellations), color="dodgerblue", fill="dodgerblue", alpha=.1, size=0.55) +
    geom_area(aes(y=bookings), color="green3", fill="green3", alpha=.1, size=0.55) +
    scale_y_continuous(
      name="Index value", 
      sec.axis = sec_axis(
        ~.*10, 
        name="Number of people", 
        breaks = seq(0, upper_bound_right_y, 500)
      ), 
      expand = c(0,0),
      breaks = seq(0, upper_bound_left_y, 50),
      limits = c(0, upper_bound_left_y)
    ) +
    scale_x_continuous(
      expand=c(0,0),
      name="",
    ) +
    theme_minimal()+ 
    theme(
      axis.line.y.right = element_line(size=0.25, colour = "black"),
      axis.line.y.left = element_line(size=0.25, colour = "black"),
      axis.line.x = element_line(size=0.25, colour = "black"),
      axis.title.y.right = element_text(angle=90, family="Times New Roman"),
    )
  # rounded_bookings <- round_any(max(data$bookings), 50, ceiling)
  # rounded_cancellations <- round_any(max(data$cancellations), 50, ceiling)
  # if (rounded_cancellations > 2 * rounded_bookings + 50) {
  #    
  # }
  break
}

country_path <- "/Users/janmelicharik/Documents/Diplomka/data/output/by_country/at/timeseries_weekly.csv"

bookings_color <- "green3"
cancellations_color <- "dodgerblue4"
covid_cases_color <- "orange3"
deaths_color <- "orangered3"

legend_details <- c(
  "Bookings per week (index, left axis)" = bookings_color,
  "Cancellations per week (index, left axis)" = cancellations_color,
  "Weekly average of new COVID-19 cases (right axis)" = covid_cases_color,
  "Deaths due to COVID-19 pew week (right axis)" = deaths_color
)

data <- read_delim(country_path, delim=",")
# NA values replaced by zeros - missing values from original data correspond
# to periods with very little or zero new COVID-19 cases or deaths
data[is.na(data["deaths"]), "deaths"] <- 0
data[is.na(data["covid_cases"]), "covid_cases"] <- 0
# Indexed values - multiplied to scale 100
data["bookings"] <- data["bookings"] * 100
data["cancellations"] <- data["cancellations"] * 100
# By definition there should not be negative values, in case there are
# it's a mistake in data input for the source and is replaced with
# absolute value
if (any(data < 0)) {
  data[data<0] <- abs(data[data<0])
}
# Calculation of scaling constant for right y axis (COVID-19 cases and deaths)
max_index <- max(data$bookings, data$cancellations)
max_cases <- max(data$covid_cases, data$deaths)
upper_bound_left_y <- round_any(max_index, 10, ceiling) + 10
upper_bound_right_y <- round_any(max_cases, 500, ceiling) + 500

scaling_cofficient <- upper_bound_left_y / upper_bound_right_y

data["covid_cases"] <- data["covid_cases"] * scaling_cofficient
data["deaths"] <- data["deaths"] * scaling_cofficient

number_of_rows = nrow(data)
x_axis_ticks <- seq(0, number_of_rows, 6)

plt <- ggplot()

country_lockdowns <- lockdowns_data[lockdowns_data$code == "at",]
# number_of_lockdowns <- nrow(country_lockdowns)
# if (number_of_lockdowns > 0) {
#   for (i in c(1:number_of_lockdowns)) {
#     plt <- plt + geom_rect(
#       aes(
#         xmin = country_lockdowns$week_start_index[i],
#         xmax = country_lockdowns$week_end_index[i],
#         ymin = 0,
#         ymax = Inf,
#       ),
#       fill = "pink",
#       alpha = 0.5
#     )
#   }
# }

plt <- plt +
  geom_rect(
    data=country_lockdowns,
    mapping=aes(
      xmin=week_start_index,
      xmax=week_end_index,
      ymin=0,
      ymax=Inf,
      fill=level
    ),
    alpha=0.5
  ) +
  geom_area(
    data = data, aes(x=0:(number_of_rows - 1), y=covid_cases, color="Weekly average of new COVID-19 cases (right axis)"),
    fill=covid_cases_color,
    alpha=.04,
    size=0.25
  ) +
  geom_area(
    aes(y=deaths, color="Deaths due to COVID-19 pew week (right axis)"),
    fill=deaths_color,
    alpha=.04,
    size=0.25
  ) +
  geom_area(
    aes(y=cancellations, color="Cancellations per week (index, left axis)"),
    fill=cancellations_color,
    alpha=.04,
    size=0.25
  ) +
  geom_area(
    aes(y=bookings, color="Bookings per week (index, left axis)"),
    fill=bookings_color,
    alpha=.12,
    size=0.65) +
  scale_color_manual(
    name="", values=legend_details
  ) +
  guides(
    color=guide_legend(
      override.aes=list(
        fill=c(
          bookings_color,
          cancellations_color,
          covid_cases_color,
          deaths_color
        ),
        alpha=.05,
        size=0.25
      )
    )
  ) +
  scale_y_continuous(
    name="Index value",
    sec.axis = sec_axis(
      ~.*10,
      name="Number of people",
      breaks = seq(0, upper_bound_right_y / scaling_cofficient, 500)
    ),
    expand = c(0,0),
    breaks = seq(0, upper_bound_left_y, 50),
    limits = c(0, max(upper_bound_left_y, upper_bound_right_y * scaling_cofficient)),
  ) +
  scale_x_continuous(
    sec.axis = sec_axis(~.*1, name=""),
    expand=c(0,0),
    name="",
    breaks = x_axis_ticks,
    labels = data$date[x_axis_ticks + 1]
  ) +
  theme_minimal() +
  theme(
    axis.line.y.right = element_line(size=0.25, colour = "black"),
    axis.line.y.left = element_line(size=0.25, colour = "black"),
    axis.line.x.bottom = element_line(size=0.25, colour = "black"),
    axis.line.x.top = element_line(size=0.25, colour = "black"),
    axis.title.y.right = element_text(angle=90, family="Times New Roman"),
    axis.title.y.left = element_text(family="Times New Roman"),
    axis.title.x = element_text(family="Times New Roman"),
    axis.text.x.bottom = element_text(angle=45, hjust = 1 ,family="Times New Roman", size=11),
    axis.text.x.top = element_blank(),
    axis.text.y = element_text(family="Times New Roman", size=11),
    panel.grid.minor = element_blank(),
    panel.grid.major = element_line(size=0.2),
    legend.position = "top",
    legend.key.size = unit(0.4, "cm"),
    legend.text = element_text(family="Times New Roman", size=11),
    legend.spacing.x = unit(0.4, "cm"),
    legend.box.spacing = unit(-.2, "cm"),
  )

plt



















