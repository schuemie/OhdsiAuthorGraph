library(dplyr)
library(xml2)
library(stringi)
library(readr)
library(jsonlite)

# entry = xml_children(root)[[1]]
extractContents <- function(entry) {
  medlineCitation <- xml_find_first(entry, "MedlineCitation")
  article <- xml_find_first(medlineCitation, "Article")
  journal <- xml_find_first(article, "Journal")
  journalIssue <- xml_find_first(journal, "JournalIssue")
  pubDate <- xml_find_first(journalIssue, "PubDate")
  content <- tibble(
    pmid = xml_text(xml_find_first(medlineCitation, "PMID")),
    year = substr(xml_text(pubDate), 1, 4),
    title = xml_text(xml_find_first(article, "ArticleTitle")),
    abstract = xml_text(xml_find_first(article, "Abstract")),
    journal = xml_text(xml_find_first(journal, "Title"))
  )
  return(content)
}
# fileName = files[[1]]
extractContentsFromXmlFile <- function(fileName) {
  root <- read_xml(fileName)
  contents <- lapply(xml_children(root), extractContents)
  contents <- bind_rows(contents)
  return(contents)
}

files <- list.files("intermediaryData", "pubmed.*.xml", full.names = TRUE)
contents <- lapply(files, extractContentsFromXmlFile)
contents <- bind_rows(contents)

contents %>%
  group_by(year) %>%
  count()

contents %>%
  group_by(journal) %>%
  summarize(paperCount = n()) %>%
  ungroup() %>%
  arrange(desc(paperCount))
