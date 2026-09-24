## My Lab Notebook for CS1066 PSet #2

PHILIP VAN TONDER

https://youtu.be/ndO9gOGjMQs

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

----

Text of my next prompt:

> Work in the directory m04. Update the script data_extraction.py. The script should extract annual revenue from both the 'RevenueFromContractWithCustomerExcludingAssessedTax' key for entries after 2018 and the other relevant revenue key for entries before 2018. 

Reflections on success/failure of this prompt:

*   The prompt was successful. The script data_extraction.py now returns data from 2016 onward as expected. 
*   The prompt was not specific regarding what key to use to extract revenue data from before 2018. This is due to my limited knowledge of US-GAAP practices and taxonomy.

----

Text of my next prompt:

> Work in the directory m04. I want to build a simple web app called financial_dashboard.py. This web app should take a CIK number as input from the user. The existing scripts, sec_data_fetch.py and data_extraction.py should be used to create a new revenue_income_asset_data.json file for the given CIK number. Using the data in revenue_income_asset_data.json, 3 plots should be generated and displayed on the dashboard showing revenue, income and asset value per year over the last 10 years. The webapp should have a simple, corporate design with blue, white and grey as the main colours and professional fonts. Use logic from the existing scripts sec_data_fetch.py and data_extraction.py as far as possible.  

Reflections on success/failure of this prompt:

*   The prompt was successful. A web app that takes a CIK number as input and shows the plots for the 3 parameters was successfully made.
*   The prompt did not specify the design of the web app beyond color and basic appearance. This was intentional and I intend to refine it going forward.
*   The prompt was highly specific in terms of what input parameters should be taken, what data should be generated and how it should be dispalyed. This followed logically from my problem decomposition and my prompting up to this point, increasing the chance of success.
*   The prompt specifies what scripts should be used to generate the displayed data. This ensured that verified working scripts were used to generate data and that the new code does not affect the functionality of any of the other scripts.  

----

> Work in the directory m04. Only change the script financial_dashboard.py. Update the styling of the webapp to use darker blues and more a more striking font for headings. Remove all radii on elements on the webpage, create a clean user interface. Make the dashboard more compact. All 3 plots should be visible without scrolling. Update the label of the y-axis to include the magnitude of dollar amounts. Update the x-axis to indicate the year for each data point. Implement a function that allows me to change the type of plot for each metric individually. Also, validate the CIK number input.

Reflections on success/failure of this prompt:

*   The prompt was successful. All refinements were implemented successfully
*   GUI changes were not exactly what I had in mind, but I do not see a reason for further refinement. The changes not meeting my expectations was due to a lack of specificity.

----

**FINAL REFLECTION:** Review your prompting work. How does your work on this pset compare with that of the first pset?

My prompting was largely successful and required minimal iteration. Giving the AI the context of the ultimate goal before asking it to solve smaller sub-problems helped ensure that each script built sensibly towards the final web app. My prompts followed the decomposition I planned at the outset, with each sub-problem handled by its own script. This allowed me to verify the output of each script before moving on and ensured that new code did not break code that was already working. My prompts were also specific about what each step needed to accomplish, which made each task easy for the AI to handle. Only two areas required iteration. The first was the revenue extraction, where the RevenueFromContractWithCustomerExcludingAssessedTax tag only exists from 2018 onward, so I had to prompt the AI to also use the older revenue tag for earlier years. The second was the GUI of the web app, which needed refinement mainly because I had not decided exactly what I wanted it to look like.

My prompting approach was similar to the first pset, but I refined it in this one. In both psets I gave the AI small subtasks to handle, but this time my prompts were more specific. I also had a clearer structure and plan for the final app before I started, which allowed me to guide the AI towards the goal more effectively.

----
----

### Handling the Problem's Whitespace

When you have a working solution, write a brief statement describing how you ultimately approached the problem's whitespace. What you might have done differently in hindsight, and why? Or defend why your work was a good approach.

I think my approach was ultimately successful, as it produced a working web app in only a few prompts with very little bug fixing. My problem decomposition followed the flow of data through the program, which allowed me to verify each new script as I went and ensured that working scripts were not affected by new code. However, because my prompts were so specific, I needed a clear idea of how I wanted to build the program before I started. Fixing bugs such as the revenue tag issue also required some independent research on my part. In the future, I could give the AI more trust to make implementation decisions and to identify issues like this one on its own, which might reduce the amount of research and planning I need to do upfront.

----
----

### Other's Review

... YOU DO NOTHING HERE; ANOTHER STUDENT WILL COMPLETE THIS PART IN SECTION ...

----
----

### AI's Review

... PASTE AI'S FEEDBACK ON THIS LAB NOTEBOOK HERE ...
