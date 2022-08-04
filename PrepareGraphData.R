# Code for downloading the data and generating files for visualizing in Cytoscape
# or the JavaScript viewer
library(dplyr)
library(xml2)
library(stringi)
library(readr)

# Start with list of PMIDs (in this case from CSV provided by Paul Nagy):
authorList <- read_csv("authorslist.csv")
pmids <- unique(authorList$pubmedID)

# Fetch article info from PubMed based on PMIDs --------------------------------
baseUrl <- "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id="
url <- paste0(baseUrl, paste(pmids, collapse = ","))
download.file(url, "intermediaryData/pubmed.xml")

# Parse XML --------------------------------------------------------------------
# Note: This code could probably be made more efficient by someone who is
# familiar with xml2

root <- read_xml("intermediaryData/pubmed.xml")
# author = authorList[[1]]
extractAuthor <- function(author) {
  tibble(
    lastName = xml_text(xml_find_first(author, "LastName")),
    firstName = xml_text(xml_find_first(author, "ForeName")),
    initials = xml_text(xml_find_first(author, "Initials"))
  ) %>%
    return()
}

# entry <- xml_children(root)[[4]]
extractAuthors <- function(entry) {
  medlineCitation <- xml_find_first(entry, "MedlineCitation")
  pmid <- xml_text(xml_find_first(medlineCitation, "PMID"))
  article <- xml_find_first(medlineCitation, "Article")
  journal <- xml_find_first(article, "Journal")
  journalIssue <- xml_find_first(journal, "JournalIssue")
  pubDate <- xml_find_first(journalIssue, "PubDate")
  year <- substr(xml_text(pubDate), 1, 4)
  authorList <- xml_find_all(xml_find_first(article, "AuthorList"), "Author")
  authors <- lapply(authorList, extractAuthor)
  authors <- bind_rows(authors) %>%
    mutate(pmid = !!pmid,
           year = !!year)
}
pmidToAuthors <- lapply(xml_children(root), extractAuthors)
pmidToAuthors <- bind_rows(pmidToAuthors) %>%
  filter(!is.na(lastName))
saveRDS(pmidToAuthors, "intermediaryData/pmidToAuthors.rds")

# Normalize authors and merge --------------------------------------------------
pmidToAuthors <- readRDS("intermediaryData/pmidToAuthors.rds")
pmidToAuthors <- pmidToAuthors %>%
  mutate(firstInitial = substr(initials, 1, 1)) %>%
  mutate(printName = paste(lastName, firstInitial, sep = ", ")) %>%
  mutate(normAuthor = tolower(stri_trans_general(printName, id = "Latin-ASCII")))

authors <- pmidToAuthors %>%
  group_by(normAuthor) %>%
  summarise(paperCount = n(),
            firstYear = min(as.numeric(year))) %>%
  inner_join(pmidToAuthors %>%
               select(normAuthor, printName) %>%
               distinct(normAuthor, .keep_all = TRUE),
             by = "normAuthor")

pmidToPrintName <- pmidToAuthors %>%
  select(pmid, normAuthor) %>%
  inner_join(authors %>%
               select(normAuthor, printName),
             by = "normAuthor") %>%
  select(pmid, printName)

links <- inner_join(
  pmidToPrintName %>%
    rename(source = printName),
  pmidToPrintName %>%
    rename(target = printName),
  by = "pmid"
) %>%
  filter(target > source) %>%
  group_by(source, target) %>%
  summarize(paperCount = n(), .groups = "drop")
saveRDS(authors, "intermediaryData/authors.rds")
saveRDS(links, "intermediaryData/links.rds")

# Output for Cytoscape ---------------------------------------------------------
authors <- readRDS("intermediaryData/authors.rds")
lines <- readRDS("intermediaryData/links.rds")

authors %>%
  select(name = printName, paperCount, firstYear) %>%
  write_tsv("cytoscape/authors.tsv")

links %>%
  write_tsv("cytoscape/links.tsv")

# Output for JavaScript viewer--------------------------------------------------
library(jsonlite)
minPaperCount <- 5

authors <- readRDS("intermediaryData/authors.rds")
links <- readRDS("intermediaryData/links.rds")

# Remove authors with too few papers:
authors <- authors %>%
  filter(paperCount >= minPaperCount)
links <- links %>%
  filter(source %in% authors$printName & target %in% authors$printName)

# Create JSON object:
nodes <- authors %>%
  select(id = printName, size = paperCount) %>%
  mutate(color = "blue")

links <- links %>%
  select(source, target, value = paperCount)

data <- list(nodes = nodes, links = links)
write_json(data, "docs/graph.json")
