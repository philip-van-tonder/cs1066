## My Lab Notebook for CS1066 PSet #2

PHILIP VAN TONDER

INSERT-YOUR-VIDEO-LINK (after completing this assignment)

----
----

### Describe Your Decomposition Approach

This problem can broadly be broken into three sub-problems. The first is obtaining the data from some source, in this case the SEC EDGAR database. The second is processing the extracted data. The third is displaying the data. My approach to breaking the specification into smaller problems will follow logically from this general statement.

I will first fetch the data from the SEC database using the SEC EDGAR API. Next, I will extract the revenue, net income and assets from the structured data obtained using the SEC EDGAR API. Finally, the revenue, net income and assets will be plotted and then displayed on a web app. Each sub-problem will be solved using its own python script. This will allow me to check the outputs for each script separately and ensure that working code is not affected by newly generated code.

----
----

### Document Your Iterations with AI

----

Text of my first prompt:

> I want to build a web based financial analysis tool that fetches data from the SEC EDGAR API and displays company revenue, net income and assets over the last 10 years. Keep this context in mind for the following prompts. I will break the problem down into sub-problems, but structure your code for each step with this end goal in mind.

Reflections on success/failure of this prompt:

*   This prompt is only to provide context to the AI about the ultimate goal of the sub-tasks that follow.

----

Text of my next prompt:

> Work in the directory m04. create a python script called sec_data_fetch.py. This script should take a 10 digit CIK number from the user. Next, it should use the CIK number and extract the company facts as a JSON file from the SEC EDGAR databse using the EDGAR API. The script should return company_data.json containing the fetched data.

Reflections on success/failure of this prompt:

*   The prompt seemed to be successful upon my initial investigation. The generated script sec_data_fetch.py produced a company_data.json file that contains the company data.
*   The script obtained the data from the SEC EDGAR API as instructed.
*   Some research was needed to identify whether the URL the AI used access the EDGAR database contained the information that I required.
*    The small scope of the prompt as well as its specificity ensured that the AI was able to easily handle the task. 

----

Text of my next prompt:

> Work in the directory m04. Create a new python script called data_extraction.py. Using the file company_data.json, retrieve the total assets from the 'assets' key, the net income from the 'NetIncomeLoss'`key, and the annual revenue from the 'RevenueFromContractWithCustomerExcludingAssessedTax' key. Data for the past 10 financial years should be extracted if available. Only extract data for full financial years, filed as forms 10-K. The output of the script should be a json file called revenue_income_asset_data.json containing the information. 

Reflections on success/failure of this prompt:

*   The prompt was successful, it proudced a .json file containing revenue, income and asset value data from the company_data.json file pulled from the SEC EDGAR API
*   data_extraction.py only contained data from 2018 onward. Upon further reseach, the revenue tag RevenueFromContractWithCustomerExcludingAssessedTax', did not exist before 2018, causing this issue.
*   Some research was needed to know what keys should be parsed for in company_data.json.
*   The small scope of the prompt as well as its specificity ensured that the AI was able to easily handle the task. Any changes could be implemented without breaking the working code. 

Text of my next prompt:

> Work in the directory m04. Update the script data_extraction.py. The script should extract annual revenue from both the 'RevenueFromContractWithCustomerExcludingAssessedTax' key for entries after 2018 and the other relevant revenue key for entries before 2018. 

Reflections on success/failure of this prompt:

*   The prompt was successful. The script data_extraction.py now returns data from 2016 onward as expected. 
*   The prompt was not specific regarding what key to use to extract revenue data from before 2018. This is due to my limited knowledge of US-GAAP practices and taxonomy.
----

**FINAL REFLECTION:** Review your prompting work. How does your work on this pset compare with that of the first pset?

... YOUR FINAL REFLECTIONS HERE ...

----
----

### Handling the Problem's Whitespace

When you have a working solution, write a brief statement describing how you ultimately approached the problem's whitespace. What you might have done differently in hindsight, and why? Or defend why your work was a good approach.

... YOUR FINAL REFLECTIONS HERE ...

----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
