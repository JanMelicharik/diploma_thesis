rm(list=ls())

library(glue)
library(ggplot2)
library(plyr)
library(readr)
library(stringr)
library(tibble)

# Constants
bookings_color <- "#0ED930"
cancellations_color <- "#4ba5f3"
covid_cases_color <- "#f45592"
deaths_color <- "#9255f4"
partial_lockdown_color <- "#ecf455"
full_lockdown_color <- "#f49f55"

legend_details <- c(
  "Bookings per week (index, left axis)" = bookings_color,
  "Cancellations per week (index, left axis)" = cancellations_color,
  "Weekly average of new COVID-19 cases (right axis)" = covid_cases_color,
  "Deaths due to COVID-19 pew week (right axis)" = deaths_color
)

legend_stripe_details <- c(
  "Full lockdown" = full_lockdown_color,
  "Partial lockdown" = partial_lockdown_color
)

lockdowns_path <- "/Users/janmelicharik/Documents/Diplomka/data/output/lockdowns.csv"

primary_alpha <- .4
secondary_alpha <- .175
tertiary_alpha <- .3

primary_size <- .65
secondary_size <- .25


lockdowns_data <- read_delim(lockdowns_path, delim=",")

OUTPUT_BY_COUNTRY_DATA_PATH <- paste(getwd(), "/data/output/by_country", sep = "")
GRAPH_OUTPUT_PATH <- paste(getwd(), "/figures/descriptive", sep = "")

for (country_path in Sys.glob(file.path(OUTPUT_BY_COUNTRY_DATA_PATH, "**/timeseries_weekly.csv")))
{
  country_code <- str_split(country_path, "/")[[1]][9]
  # Loading data
  country_data <- read_delim(country_path, delim=",")
  
  # Selection of relevant lock downs
  partial_lockdowns <- subset(lockdowns_data, code == country_code & level==1)
  full_lockdowns <- subset(lockdowns_data, code == country_code & level==2)
  
  # NA values replaced by zeros - missing values from original data correspond
  # to periods with very little or zero new COVID-19 cases or deaths
  country_data[is.na(country_data["deaths"]), "deaths"] <- 0
  country_data[is.na(country_data["covid_cases"]), "covid_cases"] <- 0
  
  # Indexed values - multiplied to scale 100
  country_data["bookings"] <- country_data["bookings"] * 100
  country_data["cancellations"] <- country_data["cancellations"] * 100
  
  # By definition there should not be negative values, in case there are
  # it's a mistake in data input for the source and is replaced with
  # absolute value
  if (any(country_data < 0)) {
    country_data[country_data<0] <- abs(country_data[country_data<0])
  }
  
  # Calculation of scaling constant for right y axis (COVID-19 cases and deaths)
  max_index <- max(country_data$bookings, country_data$cancellations)
  max_cases <- max(country_data$covid_cases, country_data$deaths)
  upper_bound_left_y <- round_any(max_index, 10, ceiling) + 10
  upper_bound_right_y <- round_any(max_cases, 500, ceiling) + 500
  
  if (max_index >= 1000) {
    prim_axis_step <- 100
  } else {
    prim_axis_step <- 50
  }
  
  if (max_cases >= 40000) {
    sec_axis_step <- 5000
  } else if (max_cases < 40000 & max_cases >= 20000) {
    sec_axis_step <- 2000
  } else if (max_cases < 20000 & max_cases >= 10000) {
    sec_axis_step <- 1000
  } else if (max_cases < 10000 & max_cases >= 4000) {
    sec_axis_step <- 500
  } else {
    sec_axis_step <- 200
  }
  
  scaling_cofficient <- upper_bound_left_y / upper_bound_right_y
  
  # Scaling data for COVID-19 cases and deaths
  country_data["covid_cases"] <- country_data["covid_cases"] * scaling_cofficient
  country_data["deaths"] <- country_data["deaths"] * scaling_cofficient
  
  # Helper constants for graph creation
  number_of_rows = nrow(country_data)
  x_axis_ticks <- seq(0, number_of_rows, 6)
  time_span <- c(0:(number_of_rows - 1))
  
  plt <- ggplot()
  
  if (nrow(full_lockdowns) > 0) {
    plt <- plt +
      geom_rect(
        data = full_lockdowns,
        mapping = aes(
          xmin = week_start_index,
          xmax = week_end_index,
          ymin = 0,
          ymax = Inf,
          fill = "Full lockdown"
        ),
        alpha = tertiary_alpha
      )
  }
  
  if (nrow(partial_lockdowns) > 0) {
    plt <- plt +
      geom_rect(
        data = partial_lockdowns,
        mapping = aes(
          xmin = week_start_index,
          xmax = week_end_index,
          ymin = 0,
          ymax = Inf,
          fill = "Partial lockdown"
        ),
        alpha = tertiary_alpha
      )
  }
    
  plt <- plt +
    geom_area(
      data = country_data,
      aes(
        x = time_span,
        y = covid_cases,
        color = "Weekly average of new COVID-19 cases (right axis)"
      ),
      fill = covid_cases_color,
      alpha = secondary_alpha,
      size = secondary_size
    ) +
    geom_area(
      data = country_data, 
      aes(
        x = time_span,
        y = cancellations, 
        color = "Cancellations per week (index, left axis)"
      ),
      fill = cancellations_color,
      alpha = secondary_alpha,
      size = secondary_size
    ) +
    geom_area(
      data = country_data, 
      aes(
        x = time_span,
        y = bookings, 
        color = "Bookings per week (index, left axis)"
      ),
      fill = bookings_color,
      alpha = primary_alpha,
      size = primary_size
    ) +
    geom_area(
      data = country_data,
      aes(
        x = time_span,
        y = deaths,
        color = "Deaths due to COVID-19 pew week (right axis)"
      ),
      fill = deaths_color,
      alpha = secondary_alpha,
      size = secondary_size
    ) +
    scale_color_manual(
      name="",
      values = legend_details
    ) +
    scale_fill_manual(
      name = "",
      values = legend_stripe_details
    ) +
    guides(
      fill = guide_legend(
        order = 2,
        nrow = 2,
        override.aes = list(
          fill = c(
            full_lockdown_color,
            partial_lockdown_color
          ),
          alpha = tertiary_alpha
        )
      ),
      color = guide_legend(
        order = 1,
        nrow = 4,
        override.aes = list(
          fill = c(
            bookings_color,
            cancellations_color,
            covid_cases_color,
            deaths_color
          ),
          alpha = secondary_alpha / 2,
          size = 0.3
        )
      )
    ) +
    scale_y_continuous(
      name = "Index value",
      sec.axis = sec_axis(
        ~./scaling_cofficient,
        name = "Number of people",
        breaks = seq(0, upper_bound_right_y / scaling_cofficient, sec_axis_step)
      ),
      expand = c(0, 0),
      breaks = seq(0, upper_bound_left_y, prim_axis_step),
      limits = c(0, max(upper_bound_left_y, upper_bound_right_y * scaling_cofficient))
    ) +
    scale_x_continuous(
      sec.axis = sec_axis(~.*1, name = ""),
      expand = c(0, 0),
      name = "",
      breaks = x_axis_ticks,
      labels = country_data$date[x_axis_ticks + 1]
    ) +
    theme_minimal() +
    theme(
      axis.line.x.bottom = element_line(size = 0.25, colour = "black"),
      axis.line.x.top = element_line(size = 0.25, colour = "black"),
      axis.text.x.bottom = element_text(angle = 45, hjust = 1 ,family = "Times New Roman", size = 11),
      axis.text.x.top = element_blank(),
      axis.title.x = element_text(family = "Times New Roman"),
      axis.line.y.right = element_line(size = 0.25, colour = "black"),
      axis.line.y.left = element_line(size = 0.25, colour = "black"),
      axis.text.y = element_text(family = "Times New Roman", size = 11),
      axis.title.y.right = element_text(angle = 90, family = "Times New Roman"),
      axis.title.y.left = element_text(family = "Times New Roman"),
      legend.box.spacing = unit(-.2, "cm"),
      legend.justification = "left",
      legend.key.size = unit(0.5, "cm"),
      legend.position = "top",
      legend.spacing.x = unit(0.4, "cm"),
      legend.spacing.y = unit(0, "cm"),
      legend.text = element_text(family = "Times New Roman", size = 11),
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(size = 0.2),
    )

  ggsave(
    filename = paste(country_code, "graph.jpg", sep="_"),
    path = GRAPH_OUTPUT_PATH,
    width = 24.7,
    height = 16,
    units = "cm"
  )
}
