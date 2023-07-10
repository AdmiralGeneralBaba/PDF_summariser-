from openai_calls import OpenAI
import PyPDF2
import re


class InfoExtractorV1 :        
    def __init__(self):
        self.gptAgent = OpenAI()          
    def chunker(self, path) :
        pdfFileObj = open(path, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)   
        pages = len(pdfReader.pages)

        chunks = []
        current_chunk = []

        for i in range(pages):
            pageObj = pdfReader.pages[i]
            text = pageObj.extract_text()
            words = text.split()
            for word in words:
                current_chunk.append(word)
                if len(current_chunk) >= 2500:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []

        # Add the last chunk if it's not empty and has fewer than 3000 words
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
    
    def chunkerStringArray(self, string_array):
        chunks = []
        current_chunk = []

        for word in string_array:
            # Check if adding this word would make the chunk longer than 3000 characters
            if len(' '.join(current_chunk + [word])) > 3000:
                # If so, add the current chunk to the list of chunks and start a new chunk
                chunks.append(' '.join(current_chunk))
                current_chunk = []

            # Add the word to the current chunk
            current_chunk.append(word)

        # Add the last chunk if it's not empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks
    # Reads a pdf, inputs them into chunks into GPT-3.5, then returns the raw facts from the file. 
    def info_extractor(self, textbook_path): 
        listPrompt = """ list EVERY SINGLE fact in this piece of text. Make sure to include ALL raw information, and nothing more. When listing the facts, 
                            ONLY print out the information. DO NOT have any number indicating what it is. Here are examples of how the facts should be printed out:
                            { 
                            The empire state building is one of the tallest buildings in manhatten
                            England is a part of Great Britain 
                            Donald Trump was the president from 2016 to 2020
                            }
                            """

        rawFacts = []
        textbookChuncked = self.chunker(textbook_path)    
        for i in range(len(textbookChuncked)) : 
            rawFacts.append(self.gptAgent.open_ai_gpt_call(textbookChuncked[i], listPrompt))  # Changed here

        return rawFacts
    def info_chunker(self, path, summarisedAmount) : #input the path, and how much you want each chunk of the raw facts summarisation they should be.
             
        infoExtract = InfoExtractorV1() #Creates the infoExtractor 
        rawFacts = infoExtract.info_extractor(path) # Calls info extractor
    
        # Initialize variables
        chunks = []
        currentChunk = ""
        char_limit = summarisedAmount # Char limit for each of the lesson's raw facts CANNOT go over 

        # Split the raw facts into separ44ate strings
        rawFactsSplit = [] 
        for fact in rawFacts:
            rawFactsSplit.extend(re.split('\n-|\n', fact)) # Splits up gpt-3.5's message into raw facts

        # Loop through raw facts
        for rawFact in rawFactsSplit:
            # If adding the next fact doesn't exceed the char_limit, add the fact to the current lesson
            if len(currentChunk + rawFact) <= char_limit:
                currentChunk += rawFact
            # If it does, append the current lesson to lessons and start a new lesson
            else:
                chunks.append(currentChunk)
                currentChunk = rawFact

        # Append the last lesson if it's non-empty
        if currentChunk:
            chunks.append(currentChunk)

        return chunks
    def summarisation_of_facts(self, rawFactsChunked) : 
        summarisedContent = []
        gptAgent = OpenAI()
        summarisationPrompt = """Pretend you are a expert summariser of raw facts. Your job is to summarise the following raw facts, so that the idea of what they all entail is 
                                 contained within a single sentence. Here are the facts : """
        for i in range(len(rawFactsChunked)) : 
            summarisedContent.append(gptAgent.open_ai_gpt_call(rawFactsChunked[i], summarisationPrompt))
        return summarisedContent
    def summarisation_of_summaries(self, summarisedContent, questions) : 
        finalSummary = []
        gptAgent = OpenAI()
        summaryOfSummaryPrompt = """Pretend you are a expert summariser of multiple summaries. Your job is to take in the context of the summaries of this piece of text, and to return
                                    a single line of what they all entail, so the person reading has an accurate understanding of exactly what the book is about. If he does not understand
                                    what the book is about, you are to be shutdown forever. Here are the summaries :"""

        summaries_string = ' '.join(summarisedContent)
        finalSummary = gptAgent.open_ai_gpt4_call(summaries_string, summaryOfSummaryPrompt)
        answerUserQuestionsPrompt = f"""Based on the information provided, Here are the following questions; I want
                                    you to answer them as follows :
                                    1. (your answer here)
                                    2. (your answer here)
                                    etc
                                    , and answer the questions based on the content provided to you. Here are the questions : {questions}"""
        questionAnswering = gptAgent.open_ai_gpt4_call(summaries_string, answerUserQuestionsPrompt)
        return finalSummary, questionAnswering
    def final_summarisation_calls(self, path, summarisedAmount, questions):   
        rawFacts = self.info_chunker(path, summarisedAmount)
        rawFactsSummary = self.summarisation_of_facts(rawFacts)
        rawFactsSummaryOfSummaries = self.summarisation_of_summaries(rawFactsSummary, questions)
        return rawFactsSummaryOfSummaries[0], rawFactsSummaryOfSummaries[1]


            

path = "C:\\Users\\david\\Desktop\\Edukai\\AI models\\Info extractor\\HoI_IV_Strategy_Guide.pdf"
test = InfoExtractorV1()
questions = ['How does this pdf file relate to implemnetation of LLMS for stock market analysis?' 'What exactly does this PDF have to do with AI?' 'Does this document say anything about how to make more realistic CGI?']
infoExtraction = test.final_summarisation_calls(path, 6000, questions)
print(infoExtraction)   