# Classifiy papers into the big four OHDSI categories using GPT-4

source("ExtractPubAbstractTitle.R")

folder <- "paperClassification"

# Have GPT-4 discuss and pick a category ---------------------------------------
library(httr)

getGpt4Response <- function(systemPrompt, prompt) {
  json <- jsonlite::toJSON(
    list(
      messages = list(
        list(
          role = "system",
          content = systemPrompt
        ),
        list(
          role = "user",
          content = prompt
        ),
        list(
          role = "assistant",
          content = ""
        )
      ),
      temperature = 0.00000001,
      frequency_penalty = 0,
      presence_penalty = 0,
      max_tokens = 4096
    ),
    auto_unbox = TRUE
  )

  startTime <- Sys.time()
  response <- POST(
    url = keyring::key_get("genai_gpt4_endpoint"),
    body = json,
    add_headers("Content-Type" = "application/json",
                "api-key" = keyring::key_get("genai_api_gpt4_key"))
  )
  delta <- Sys.time() - startTime
  message(sprintf("- Generating response took %0.1f %s", delta, attr(delta, "units")))
  result <- content(response, "text", encoding = "UTF-8")
  result <- jsonlite::fromJSON(result)
  text <- result$choices$message$content
  return(text)
}

systemPrompt <- "
Please classify the following OHDSI publication into one of the four collaboration categories of the OHDSI open science community. The categories are:

1. **Open community data standards**: Maintaining the OMOP common data model, OHDSI standardized vocabularies, and community conventions for extract-transform-load (ETL) and data quality assessment.
2. **Methodological research**: Developing and empirically evaluating analytic approaches to determine scientific best practices in statistics, epidemiology, and informatics.
3. **Open source development**: Creating software tools that codify best practices and enable the community to execute analyses through consistent and reproducible processes.
4. **Clinical evidence generation**: Conducting network studies to test clinical hypotheses and produce evidence characterizing disease natural history and treatment utilization, estimating effects of medical interventions for safety surveillance and comparative effectiveness, and predicting outcomes for disease interception and precision medicine.

First, discuss the potential category or categories that might apply to the publication. Then, select exactly one category that is most appropriate based on the topic that best represents the content of the article.

Output format:
Discussion: [Your discussion here]
Final category: [Selected category here, exactly one of 1, 2, 3, or 4]

Classify the following OHDSI publication:
"

for (i in 1:nrow(contents)) {
  writeLines(sprintf("Processing paper %d of %d", i, nrow(contents)))
  responseFileName <- file.path(folder, sprintf("Response_pmid%s.txt", contents$pmid[i]))
  if (!file.exists(responseFileName)) {
    prompt <- paste("Title:", contents$title[i])
    if (!is.na(contents$abstract[i])) {
      prompt <- paste(prompt,
                      paste("Abstract:", contents$abstract[i]),
                      sep = "\n\n")
    }
    prompt <- paste(prompt,
                    paste("Journal:", contents$journal[i]),
                    sep = "\n\n")
    if (nchar(prompt) > 10000) {
      writeLines(sprintf("Skipping pmid %s because text too long", contents$pmid[i]))
    } else {
      response <- getGpt4Response(systemPrompt, prompt)
      writeLines(response)
      writeLines(response, responseFileName)
    }
  }
}

# Parse GPT-4 output -----------------------------------------------------------
library(stringr)
responseFiles <- list.files("paperClassification", "Response_pmid.*")
results <- tibble(
  pmid = gsub("Response_pmid", "", gsub("\\.txt", "", responseFiles)),
  number = NA,
  category = as.character(NA)
)
responseFile = responseFiles[1]
for (i in seq_along(responseFiles)) {
  responseFile <- responseFiles[i]
  response <- paste(readLines(file.path(folder, responseFile), encoding = "latin1"), collapse = "\n")
  category <- gsub("^.*Final category", "", response)
  number <- str_extract(category, "\\d")
  if (is.na(category)) {
    number <- case_when(
      grepl("standard", category, ignore.case = TRUE) ~ "1",
      grepl("method", category, ignore.case = TRUE) ~ "2",
      grepl("source", category, ignore.case = TRUE) ~ "3",
      grepl("evidence", category, ignore.case = TRUE) ~ "4",
      TRUE ~ NA)
  }
  label <- case_when(number == "1" ~ "Open community data standards",
                     number == "2" ~ "Methodological research",
                     number == "3" ~ "Open source development",
                     number == "4" ~ "Clinical evidence generation",
                     TRUE ~ "Unknown")
  results$number[i] <- number
  results$category[i] <- label
}
which(is.na(results$category))
i = 100

results <- contents %>%
  select(pmid, year, title) %>%
  inner_join(results %>%
               select(pmid, category),
             by = join_by(pmid))

results %>%
  group_by(category) %>%
  summarize(paperCount = n()) %>%
  ungroup() %>%
  arrange(desc(paperCount))

readr::write_csv(results, file.path(folder, "PaperClassifications.csv"))

# Join to authors --------------------------------------------------------------
library(tidyr)
library(dplyr)
classifications <- readr::read_csv(file.path(folder, "PaperClassifications.csv"), show_col_types = FALSE)
pmidToAuthors <- readRDS("intermediaryData/pmidToAuthors.rds")

authorClassification <- classifications %>%
  mutate(pmid = as.character(pmid)) %>%
  filter(category != "Unknown") %>%
  inner_join(pmidToAuthors, by = join_by(pmid)) %>%
  mutate(value = 1) %>%
  select(author = printName, category, value) %>%
  group_by(author, category) %>%
  summarize(value = sum(value, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(names_from = category, values_from = value, values_fill = 0) %>%
  ungroup() %>%
  mutate(paperCount = rowSums(across(2:5))) %>%
  arrange(desc(paperCount))
readr::write_csv(authorClassification, file.path(folder, "AuthorClassifications.csv"))


# Try color plotting -----------------------------------------------------------
library(ggplot2)
rybToRgb <- function(r, y, b) {
  ## Deconstruct to vectors
  R.ryb = r
  Y.ryb = y
  B.ryb = b
  ## Remove black
  I.b   = pmin(R.ryb,Y.ryb,B.ryb)
  r.ryb = R.ryb - I.b
  y.ryb = Y.ryb - I.b
  b.ryb = B.ryb - I.b
  ## Calculate rgb values
  r.rgb = r.ryb + y.ryb - pmin(y.ryb,b.ryb)
  g.rgb = y.ryb + pmin(y.ryb,b.ryb)
  b.rgb = 2 * (b.ryb - pmin(y.ryb,b.ryb))
  ## Normalise (p=prime symbol)
  n = pmax(r.rgb,g.rgb,b.rgb) / pmax(r.ryb,y.ryb,b.ryb)
  n[n==0] = 1 ## for cases when n=0
  rp.rgb = r.rgb / n
  gp.rgb = g.rgb / n
  bp.rgb = b.rgb / n
  ## Add white component
  I.w   = pmin(1-R.ryb,1-Y.ryb,1-B.ryb)
  R.rgb = rp.rgb + I.w
  G.rgb = gp.rgb + I.w
  B.rgb = bp.rgb + I.w
  RGB   = rgb(red=R.rgb, green=G.rgb, blue=B.rgb)
  return(RGB)
}

authorColors <- authorClassification %>%
  mutate(
    color = rgb(
      `Open community data standards`/paperCount,
      `Clinical evidence generation`/paperCount,
      (`Open source development` + `Methodological research`)/paperCount
    ),
    rn = row_number())

ggplot(authorColors[1:50, ], aes(y=rn, color = color)) +
  geom_point(x = 0.1, size = 6) +
  geom_text(aes(label = author), x = 0.12, hjust = 0) +
  scale_color_identity()

ggplot(authorColors[1:500, ], aes(x = runif(500), y = runif(500), color = color)) +
  geom_point(size = 6, alpha = 0.8) +
  geom_text(aes(label = author),  hjust = 0.5, color = "black") +
  scale_color_identity()

