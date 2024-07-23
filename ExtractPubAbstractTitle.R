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
    abstract = xml_text(xml_find_first(article, "Abstract"))
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

# Create word cloud per year -----------------------------------------------------------------------
contents <- contents %>%
  filter(as.integer(year) >= 2014)

# Install and load the necessary packages
install.packages("tm")
install.packages("wordcloud")
install.packages("RColorBrewer")
library(tm)
library(wordcloud)
library(RColorBrewer)


for (year in unique(contents$year)) {
  texts <- contents %>%
    filter(year == !!year) %>%
    mutate(text = paste(title, abstract)) %>%
    pull(text)
  corpus <- Corpus(VectorSource(texts))
  corpus <- tm_map(corpus, content_transformer(tolower))
  corpus <- tm_map(corpus, removePunctuation)
  corpus <- tm_map(corpus, removeNumbers)
  corpus <- tm_map(corpus, removeWords, stopwords("english"))
  tdm <- TermDocumentMatrix(corpus)
  m <- as.matrix(tdm)
  word_freqs <- sort(rowSums(m), decreasing=TRUE)
  df <- data.frame(word=names(word_freqs), freq=word_freqs)
  png(file.path("yearlyWordClouds", sprintf("words_%s.png", year)), width = 800, height = 800)
  par(mar = c(0, 0, 0, 0))
  wordcloud(words = df$word,
            freq = df$freq,
            min.freq = 1,
            max.words=200,
            random.order=FALSE,
            rot.per=0.35,
            scale = c(3, 1.5),
            colors=brewer.pal(8, "Dark2"))
  dev.off()
}

