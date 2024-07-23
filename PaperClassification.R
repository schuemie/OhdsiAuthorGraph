# Classifiy papers into the big four OHDSI categories using GPT-4

source("ExtractPubAbstractTitle.R")

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
    responseFileName <- file.path("paperClassification", sprintf("Response_pmid%s.txt", contents$pmid[i]))
    prompt <- paste("Title:", contents$title[i])
    if (!is.na(contents$abstract[i])) {
      prompt <- paste(prompt,
                      paste("Abstract:", contents$abstract[i]),
                      sep = "\n\n")
    }
    prompt <- paste(prompt,
                    paste("Journal:", contents$journal[i]),
                    sep = "\n\n")

    response <- getGpt4Response(systemPrompt, prompt)
    writeLines(response)
    writeLines(response, responseFileName)
}
